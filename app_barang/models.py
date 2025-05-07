from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class Pemasok(models.Model):
    kode = models.CharField(max_length=50, null=False, unique=True)
    nama = models.CharField(max_length=100, null=False, blank=False)
    alamat = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"{self.kode} - {self.nama}"
    
class Gudang(models.Model):
    kode = models.CharField(max_length=50, null=False, unique=True)
    nama = models.CharField(max_length=100, null=False, blank=False)
    alamat = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"{self.kode} - {self.nama}"
    
class Barang(models.Model):
    TIPE_CHOICES = [
        ('G', 'General'),
        ('D', 'Detail'),
    ]

    kode = models.CharField(max_length=50, null=False, unique=True)
    nama = models.CharField(max_length=100, null=False, blank=False)
    tipe = models.CharField(max_length=1, choices=TIPE_CHOICES, null=False, blank=False)
    level = models.IntegerField(null=False, blank=False)
    induk = models.CharField(max_length=50, null=True, blank=True)
    satuan = models.CharField(max_length=20, null=True, blank=True)
    harga = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    qty_stok = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.kode} - {self.nama}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (1 <= self.level <= 9):
            raise ValidationError({'level': 'Level harus antara 1 sampai 9.'})
        
class PO(models.Model):
    nomor_po = models.CharField(max_length=50, unique=True, null=False, blank=False)
    tanggal = models.DateField(null=False, blank=False)
    pemasok = models.ForeignKey(Pemasok, on_delete=models.PROTECT, null=False)
    gudang = models.ForeignKey(Gudang, on_delete=models.PROTECT, null=False)
    alamat_kirim = models.TextField(null=False, blank=False)
    kode_barang = models.ForeignKey(Barang, on_delete=models.PROTECT, null=False)
    qty_po = models.PositiveIntegerField(null=False)
    harga = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    qty_terima = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"PO {self.nomor_po}"

    def clean(self):
        if self.tanggal > timezone.now().date():
            raise ValidationError({'tanggal': 'Tanggal tidak boleh lebih dari hari ini.'})
        if self.qty_po <= 0:
            raise ValidationError({'qty_po': 'Qty harus lebih dari 0.'})
        
class TerimaBarang(models.Model):
    nomor_terima = models.CharField(max_length=50, unique=True, null=False)
    tanggal = models.DateField(null=False)
    nomor_po = models.ForeignKey(PO, on_delete=models.PROTECT, null=False)
    pemasok = models.CharField(max_length=100, null=False, blank=False)
    gudang = models.CharField(max_length=100, null=False, blank=False)
    kode_barang = models.CharField(max_length=100, null=False, blank=False)
    qty_terima = models.PositiveIntegerField(null=False)

    def __str__(self):
        return f"Terima {self.nomor_terima} - {self.kode_barang}"

    def clean(self):
        errors = {}

        if self.tanggal > timezone.now().date():
            errors['tanggal'] = 'Tanggal tidak boleh lebih dari hari ini.'

        if self.qty_terima <= 0:
            errors['qty_terima'] = 'Qty terima harus lebih dari 0.'

        if self.nomor_po:
            if self.kode_barang != self.nomor_po.kode_barang.kode:
                errors['kode_barang'] = 'Kode barang tidak sesuai dengan yang ada di PO.'
            if self.pemasok != self.nomor_po.pemasok.nama:
                errors['pemasok'] = 'Pemasok tidak sesuai dengan PO.'
            if self.gudang != self.nomor_po.gudang.nama:
                errors['gudang'] = 'Gudang tidak sesuai dengan PO.'

            total_terima = TerimaBarang.objects.filter(nomor_po=self.nomor_po, kode_barang=self.kode_barang).exclude(pk=self.pk).aggregate(
                total=models.Sum('qty_terima'))['total'] or 0

            if total_terima + self.qty_terima > self.nomor_po.qty_po:
                errors['qty_terima'] = f'Total qty terima melebihi qty PO ({self.nomor_po.qty_po}). Sudah diterima: {total_terima}.'

        if errors:
            raise ValidationError(errors)