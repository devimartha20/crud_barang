from django import forms
from .models import Pemasok, Gudang, Barang, PO, TerimaBarang
from django.db import models

class PemasokForm(forms.ModelForm):
    class Meta:
        model = Pemasok
        fields = ['kode', 'nama', 'alamat']
        widgets = {
            'kode': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control'}),
        }

class GudangForm(forms.ModelForm):
    class Meta:
        model = Gudang
        fields = ['kode', 'nama', 'alamat']
        widgets = {
            'kode': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control'}),
        }
LEVEL_CHOICES = [(i, str(i)) for i in range(1, 10)]
class BarangForm(forms.ModelForm):
    class Meta:
        model = Barang
        fields = ['kode', 'nama', 'tipe', 'level', 'induk', 'satuan', 'harga']
        widgets = {
            'kode': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'tipe': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(choices=LEVEL_CHOICES, attrs={'class': 'form-control'}),
            'induk': forms.Select(attrs={'class': 'form-control'}),
            'satuan': forms.TextInput(attrs={'class': 'form-control'}),
            'harga': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    # Validasi custom menggunakan clean()
    def clean(self):
        cleaned_data = super().clean()
        tipe = cleaned_data.get('tipe')
        level = cleaned_data.get('level')
        induk = cleaned_data.get('induk')
        satuan = cleaned_data.get('satuan')
        harga = cleaned_data.get('harga')
        
        # Validasi jika tipe adalah 'G' dan level == 1
        if tipe == 'G' and level == '1':
            if satuan is not None or harga is not None:
                raise forms.ValidationError("Satuan dan Harga tidak boleh diisi jika Tipe G dan Level 1")
        
        # Validasi jika tipe adalah 'G' dan level > 1
        elif tipe == 'G' and int(level) > 1:
            if induk is None:
                raise forms.ValidationError("Induk Barang wajib diisi jika Tipe G dan Level > 1")
        
        # Validasi jika tipe adalah 'D'
        elif tipe == 'D':
            if satuan is None or harga is None:
                raise forms.ValidationError("Satuan dan Harga wajib diisi jika Tipe D")
            if harga < 0:
                raise forms.ValidationError("Harga harus lebih dari 0")
        
        return cleaned_data

class POForm(forms.ModelForm):
    class Meta:
        model = PO
        fields = ['nomor_po', 'tanggal', 'pemasok', 'gudang', 'alamat_kirim', 'kode_barang', 'qty_po', 'harga']
        widgets = {
            'nomor_po': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pemasok': forms.Select(attrs={'class': 'form-control'}),
            'gudang': forms.Select(attrs={'class': 'form-control'}),
            'alamat_kirim': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'readonly':'readonly'}),
            'kode_barang': forms.Select(attrs={'class': 'form-control'}),
            'qty_po': forms.NumberInput(attrs={'class': 'form-control'}),
            'harga': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
    kode_barang = forms.ModelChoiceField(
        queryset=Barang.objects.filter(tipe='D'),
        empty_label="Pilih Barang",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class TerimaBarangForm(forms.ModelForm):
    class Meta:
        model = TerimaBarang
        fields = ['nomor_terima', 'tanggal', 'nomor_po', 'pemasok', 'gudang', 'kode_barang', 'qty_terima']
        widgets = {
        'nomor_terima': forms.TextInput(attrs={'class': 'form-control'}),
        'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'pemasok': forms.TextInput(attrs={'class': 'form-control', 'readonly':'readonly'}),
        'gudang': forms.TextInput(attrs={'class': 'form-control', 'readonly':'readonly'}),
        'kode_barang': forms.TextInput(attrs={'class': 'form-control', 'readonly':'readonly'}),
        'qty_terima': forms.NumberInput(attrs={'class': 'form-control'}),
    }
    
    nomor_po = forms.ModelChoiceField(
        queryset=PO.objects.filter(qty_terima__lt=models.F('qty_po')),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
