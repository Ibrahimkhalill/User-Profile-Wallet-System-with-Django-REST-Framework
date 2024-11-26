from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer,WalletSerializer,TransactionSerializer
from .models import Wallet,Transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    dob = request.data.get('dob')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=400)

    # Create user
    user = User.objects.create_user(username=username, password=password, email=email)
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    # Create the UserProfile object
    userProfile = UserProfile(user=user, first_name=first_name, last_name=last_name, email=email, dob=dob)
    userProfile.save()

    Wallet.objects.create(user=user)

    return Response({'message': 'User registered successfully'}, status=201)




@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
       
        serializer = UserProfileSerializer(profile, data=request.data, partial=(request.method == 'PATCH'))

        if request.FILES.get('profile_picture'):
          
            profile.profile_picture = request.FILES['profile_picture']
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)



@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def wallet_view(request):
    wallet = get_object_or_404(Wallet, user=request.user)

    if request.method == 'GET':
        # Serialize the wallet data
        wallet_serializer = WalletSerializer(wallet)

        # Get the last 5 transactions
        transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:5]
        transaction_serializer = TransactionSerializer(transactions, many=True)

        return Response({
            'balance': wallet_serializer.data,
            'transactions': transaction_serializer.data
        })

    elif request.method == 'POST':
        # Add funds to wallet
        amount = Decimal(request.data.get('balance', 0))
        
        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=400)

        wallet.balance += amount
        wallet.save()

        # Record the transaction
        Transaction.objects.create(wallet=wallet, amount=amount, transaction_type=Transaction.DEPOSIT)

        wallet_serializer = WalletSerializer(wallet)
        return Response({'message': 'Funds added successfully', 'balance': wallet_serializer.data})

    elif request.method == 'PATCH':
        # substruct funds from the wallet
        amount = Decimal(request.data.get('amount', 0))

        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=400)

        if wallet.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=400)

        wallet.balance -= amount
        wallet.save()

        # Record the transaction
        Transaction.objects.create(wallet=wallet, amount=amount, transaction_type=Transaction.WITHDRAWAL)

        wallet_serializer = WalletSerializer(wallet)
        return Response({'message': 'Funds substruct successfully', 'balance': wallet_serializer.data})
