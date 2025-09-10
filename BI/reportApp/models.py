# external_data/models.py
from django.db import models

class AccountBase(models.Model):
    account_number = models.CharField(max_length=50, primary_key=True)
    customer_no = models.CharField(max_length=50, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    sector_name = models.CharField(max_length=200, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    industry_name = models.CharField(max_length=200, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    working_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    opening_date = models.DateField(blank=True, null=True)
    branch_code = models.CharField(max_length=20, blank=True, null=True)
    branch_name = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    ultimate_ben = models.CharField(max_length=255, blank=True, null=True)
    cust_type = models.CharField(max_length=50, blank=True, null=True)
    report_date = models.DateField(blank=True, null=True)
    report_time = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False  # Crucial: tells Django not to manage this table
        db_table = 'account_base'  # Actual table name in database
        verbose_name = 'Account Base'
        verbose_name_plural = 'Account Base Records'

    def __str__(self):
        return f"{self.account_number} - {self.customer_name}"