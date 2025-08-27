from import_export import resources
from .models import Receipt

class ReceiptResource(resources.ModelResource):
    class Meta:
        model = Receipt
        fields = ('date', 'vendor', 'category', 'amount')
        export_order = ('date', 'vendor', 'category', 'amount')