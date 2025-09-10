# reportApp/serializers.py
from rest_framework import serializers
from .models import AccountBase
from decimal import Decimal, InvalidOperation

class SafeDecimalField(serializers.DecimalField):
    """A DecimalField that converts invalid inputs to 0."""
    def to_representation(self, value):
        try:
            if value in [None, '']:
                return Decimal('0.00')
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal('0.00')

class AccountBaseSerializer(serializers.ModelSerializer):
    working_balance = SafeDecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = AccountBase
        fields = '__all__'

class AccountBaseSummarySerializer(serializers.ModelSerializer):
    working_balance = SafeDecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = AccountBase
        fields = [
        #     'account_number', 
        #     'customer_name', 
        #     'customer_no',
        #     'phone_number',
        #     'working_balance',
        #     'currency',
        #     'branch_name',
        #     'product_name'
        # 
        
"account_number",
"customer_no",
"customer_name",
"phone_number",
"category",
"product_name",
"sector",
"sector_name",
"industry",
"industry_name",
"currency",
"working_balance",
"opening_date",
"branch_code",
"branch_name",
"region",
"ultimate_ben",
"cust_type",
"report_date",
"report_time"]