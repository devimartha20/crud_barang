from django.shortcuts import render, get_object_or_404, redirect
from .models import Pemasok, Gudang, PO, TerimaBarang, Barang
from .forms import PemasokForm, GudangForm, POForm, TerimaBarangForm, BarangForm
from django.http import JsonResponse

def pemasok_list(request):
    pemasoks = Pemasok.objects.all()
    if request.method == 'POST':
        form = PemasokForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect('pemasok_list')  
    else:
        form = PemasokForm()

    # Kirim data pemasok dan form ke template
    return render(request, 'app_barang/pemasok/pemasok_list.html', {'pemasoks': pemasoks, 'form': form})

def pemasok_update(request, pk):
    pemasok = get_object_or_404(Pemasok, pk=pk)
    if request.method == 'POST':
        form = PemasokForm(request.POST, instance=pemasok)
        if form.is_valid():
            form.save()
            return redirect('pemasok_list')
    else:
        form = PemasokForm(instance=pemasok)
    return render(request, 'app_barang/pemasok/pemasok_edit.html', {'form': form, 'pemasok': pemasok})

def pemasok_delete(request, pk):
    pemasok = get_object_or_404(Pemasok, pk=pk)
    if request.method == 'POST':
        pemasok.delete()
    return redirect('pemasok_list')

def gudang_list(request):
    gudangs = Gudang.objects.all()

    if request.method == 'POST':
        form = GudangForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gudang_list') 
    else:
        form = GudangForm()

    return render(request, 'app_barang/gudang/gudang_list.html', {'gudangs': gudangs, 'form': form})

def gudang_update(request, pk):
    gudang = get_object_or_404(Gudang, pk=pk)
    if request.method == 'POST':
        form = GudangForm(request.POST, instance=gudang)
        if form.is_valid():
            form.save()
            return redirect('gudang_list')
    else:
        form = GudangForm(instance=gudang)
    return render(request, 'app_barang/gudang/gudang_edit.html', {'form': form, 'gudang': gudang})

def gudang_delete(request, pk):
    gudang = get_object_or_404(Gudang, pk=pk)
    if request.method == 'POST':
        gudang.delete()
    return redirect('gudang_list')

def barang_create(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('barang_list')
    else:
        form = BarangForm()
    
    return render(request, 'app_barang/barang/barang_create.html', {'form': form})

def barang_list(request):
    barangs = Barang.objects.all()
    return render(request, 'app_barang/barang/barang_list.html', {'barangs': barangs})

def barang_update(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    if request.method == 'POST':
        form = BarangForm(request.POST, instance=barang)
        if form.is_valid():
            form.save()
            return redirect('barang_list')  
    else:
        form = BarangForm(instance=barang)
    
    return render(request, 'app_barang/barang/barang_edit.html', {'form': form, 'barang': barang})

def barang_delete(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    if request.method == 'POST':
        barang.delete()
        return redirect('barang_list') 
    return render(request, 'app_barang/barang/barang_list.html', {'barang': barang})

def get_induk_barang(request):
    try:
        level = int(request.GET.get('level', 0))
        tipe = request.GET.get('tipe')
    except (ValueError, TypeError):
        return JsonResponse({'data': []})

    if tipe == 'G' and level > 1 or tipe == 'D':
        barang_list = Barang.objects.filter(level=level - 1)
    else:
        return JsonResponse({'data': []})  # Induk tidak diperlukan

    data = [{'id': b.id, 'kode': b.kode} for b in barang_list]
    return JsonResponse({'data': data})

# PO (Purchase Order) 
def po_list(request):
    pos = PO.objects.all()
    return render(request, 'app_barang/po/po_list.html', {'pos': pos})

def po_create(request):
    if request.method == 'POST':
        form = POForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('po_list')
    else:
        form = POForm()
    return render(request, 'app_barang/po/po_create.html', {'form': form})

def po_update(request, pk):
    po = get_object_or_404(PO, pk=pk)
    if request.method == 'POST':
        form = POForm(request.POST, instance=po)
        if form.is_valid():
            form.save()
            return redirect('po_list')
    else:
        form = POForm(instance=po)
    return render(request, 'app_barang/po/po_edit.html', {'form': form})

def po_delete(request, pk):
    po = get_object_or_404(PO, pk=pk)
    if request.method == 'POST':
        po.delete()
        return redirect('po_list')
    return render(request, 'app_barang/po/po_list.html', {'po': po})

def get_gudang_alamat(request):
    gudang_id = request.GET.get('gudang_id')
    alamat = ''
    if gudang_id:
        try:
            gudang = Gudang.objects.get(id=gudang_id)
            alamat = gudang.alamat
        except Gudang.DoesNotExist:
            pass
    return JsonResponse({'alamat': alamat})

def get_barang_harga(request):
    barang_id = request.GET.get('barang_id')
    harga = ''
    if barang_id:
        try:
            barang = Barang.objects.get(id=barang_id)
            harga = str(barang.harga) if barang.harga else ''
        except Barang.DoesNotExist:
            pass
    return JsonResponse({'harga': harga})

# TerimaBarang 
def terima_barang_list(request):
    terima_barangs = TerimaBarang.objects.all()
    return render(request, 'app_barang/terima_barang/terima_barang_list.html', {'terima_barangs': terima_barangs})

def terima_barang_create(request):
    if request.method == 'POST':
        form = TerimaBarangForm(request.POST)
        if form.is_valid():
            terima_barang = form.save(commit=False)

      
            po = terima_barang.nomor_po

          
            total_qty_terima = po.qty_terima + terima_barang.qty_terima
            if total_qty_terima > po.qty_po:
                form.add_error('qty_terima', 'Qty terima melebihi jumlah PO.')
            else:
                po.qty_terima = total_qty_terima
                po.save()

                terima_barang.save()
                return redirect('terima_barang_list')
            return redirect('terima_barang_list')
    else:
        form = TerimaBarangForm()
    return render(request, 'app_barang/terima_barang/terima_barang_create.html', {'form': form})

def terima_barang_update(request, pk):
    terima_barang = get_object_or_404(TerimaBarang, pk=pk)
    if request.method == 'POST':
        form = TerimaBarangForm(request.POST, instance=terima_barang)
        if form.is_valid():
            terima_barang = form.save(commit=False)

    
            po = terima_barang.nomor_po

        
            total_qty_terima = terima_barang.qty_terima
            if total_qty_terima > po.qty_po:
                form.add_error('qty_terima', 'Qty terima melebihi jumlah PO.')
            else:
                po.qty_terima = total_qty_terima
                po.save()

                terima_barang.save()
            return redirect('terima_barang_list')  
         
    else:
        form = TerimaBarangForm(instance=terima_barang)
    return render(request, 'app_barang/terima_barang/terima_barang_edit.html', {'form': form})

def terima_barang_delete(request, pk):
    terima_barang = get_object_or_404(TerimaBarang, pk=pk)
    if request.method == 'POST':
        terima_barang.delete()
        return redirect('terima_barang_list')
    return render(request, 'app_barang/terima_barang/terima_barang_list.html', {'terima_barang': terima_barang})

def get_barang_by_po(request):
    po_id = request.GET.get('po_id')
    try:
        po = PO.objects.get(id=po_id)
        
        data = {
            'kode_barang': po.kode_barang.kode,
            'gudang': po.gudang.nama,  
            'pemasok': po.pemasok.nama,
            'qty_po' : po.qty_po
        }
        
        return JsonResponse({'data': [data]})
    except PO.DoesNotExist:
        return JsonResponse({'data': []})
