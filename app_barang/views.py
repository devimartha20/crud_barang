from django.shortcuts import render, get_object_or_404, redirect
from .models import Pemasok, Gudang, PO, TerimaBarang, Barang
from .forms import PemasokForm, GudangForm, POForm, TerimaBarangForm, BarangForm
from django.http import JsonResponse, HttpResponse
from django.db import models
from django.db.models import Case, When, Value, CharField
from django.db.models import F

def pemasok_list(request):
    pemasoks = Pemasok.objects.all()
    pemasok_dipakai = {
        p.id: PO.objects.filter(pemasok=p).exists()
        for p in pemasoks
    }
    print(pemasok_dipakai)
    if request.method == 'POST':
        form = PemasokForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect('pemasok_list')  
    else:
        form = PemasokForm()

    return render(request, 'app_barang/pemasok/pemasok_list.html', {
        'pemasoks': pemasoks, 
        'pemasok_dipakai': pemasok_dipakai,
        'form': form
        })
    
def pemasok_detail(request, pk):
    pemasok = get_object_or_404(Pemasok, pk=pk)
    po_terkait = PO.objects.filter(pemasok=pemasok).select_related('kode_barang', 'gudang')
    return render(request, 'app_barang/pemasok/pemasok_detail.html', {
        'pemasok': pemasok,
        'po_terkait': po_terkait,
    })

def pemasok_update(request, pk):
    pemasok = get_object_or_404(Pemasok, pk=pk)
    pemasok_dipakai = PO.objects.filter(pemasok=pemasok).exists()
    if not pemasok_dipakai:
        if request.method == 'POST':
            form = PemasokForm(request.POST, instance=pemasok)
            if form.is_valid():
                form.save()
                return redirect('pemasok_list')
        else:
            form = PemasokForm(instance=pemasok)
        return render(request, 'app_barang/pemasok/pemasok_edit.html', {'form': form, 'pemasok': pemasok})
    else:
        return HttpResponse('Maaf pemasok tidak dapat dimodifikasi karena telah digunakan oleh PO')

def pemasok_delete(request, pk):
    pemasok = get_object_or_404(Pemasok, pk=pk)
    pemasok_dipakai = PO.objects.filter(pemasok=pemasok).exists()
    if not pemasok_dipakai:
        if request.method == 'POST':
            pemasok.delete()
        return redirect('pemasok_list')
    else:
        return HttpResponse('Maaf pemasok tidak dapat dihapus karena telah digunakan oleh PO')

def gudang_list(request):
    gudangs = Gudang.objects.all()
    gudang_dipakai = {
        p.id: PO.objects.filter(gudang=p).exists()
        for p in gudangs
    }
    if request.method == 'POST':
        form = GudangForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gudang_list') 
    else:
        form = GudangForm()

    return render(request, 'app_barang/gudang/gudang_list.html', {
        'gudangs': gudangs, 
        'form': form,
        'gudang_dipakai': gudang_dipakai
        })
    
def gudang_detail(request, pk):
    gudang = get_object_or_404(Gudang, pk=pk)
    po_terkait = PO.objects.filter(gudang=gudang).select_related('kode_barang', 'pemasok')
    return render(request, 'app_barang/gudang/gudang_detail.html', {
        'gudang': gudang,
        'po_terkait': po_terkait,
    })

def gudang_update(request, pk):
    gudang = get_object_or_404(Gudang, pk=pk)
    gudang_dipakai = PO.objects.filter(gudang=gudang).exists()
    if not gudang_dipakai:
        if request.method == 'POST':
            form = GudangForm(request.POST, instance=gudang)
            if form.is_valid():
                form.save()
                return redirect('gudang_list')
        else:
            form = GudangForm(instance=gudang)
        return render(request, 'app_barang/gudang/gudang_edit.html', {'form': form, 'gudang': gudang})
    else:
        return HttpResponse('Maaf gudang tidak dapat dimodifikasi karena telah digunakan oleh PO')

def gudang_delete(request, pk):
    gudang = get_object_or_404(Gudang, pk=pk)
    gudang_dipakai = PO.objects.filter(gudang=gudang).exists()
    if not gudang_dipakai:
        if request.method == 'POST':
            gudang.delete()
        return redirect('gudang_list')
    else:
        return HttpResponse('Maaf gudang tidak dapat dihapus karena telah digunakan oleh PO')

def barang_create(request):
    if request.method == 'POST':
        form = BarangForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('barang_list')
    else:
        form = BarangForm()
    
    return render(request, 'app_barang/barang/barang_form.html', {'form': form})

def barang_list(request):
    barangs = Barang.objects.annotate(
        induk_order=Case(
            When(induk__isnull=True, then=F('kode')),
            default=F('induk'),
            output_field=CharField()
        )
    ).order_by('kode','induk_order', '-tipe', 'level')
    used_as_induk_kodes = set(Barang.objects.exclude(induk__isnull=True).values_list('induk', flat=True))
    used_in_po_ids = set(PO.objects.values_list('kode_barang_id', flat=True))
    return render(request, 'app_barang/barang/barang_list.html', {
        'barangs': barangs,
        'used_as_induk_kodes': used_as_induk_kodes,
        'used_in_po_ids': used_in_po_ids,
    })

def barang_update(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    used_as_induk = Barang.objects.exclude(induk__isnull=True).filter(induk=barang.kode).exists()
    used_in_po = PO.objects.filter(kode_barang=barang).exists()
    if not used_as_induk and not used_in_po:
        if request.method == 'POST':
            form = BarangForm(request.POST, instance=barang)
            if form.is_valid():
                form.save()
                return redirect('barang_list')  
        else:
            form = BarangForm(instance=barang)
    
        return render(request, 'app_barang/barang/barang_form.html', {'form': form, 'barang': barang})
    else:
        return HttpResponse('Maaf barang tidak dapat dimodifikasi karena telah digunakan oleh PO atau sebagai induk barang lain')

def barang_delete(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    used_as_induk = Barang.objects.exclude(induk__isnull=True).filter(induk=barang.kode).exists()
    used_in_po = PO.objects.filter(kode_barang=barang).exists()
    if not used_as_induk and not used_in_po:
        if request.method == 'POST':
            barang.delete()
            return redirect('barang_list') 
        return render(request, 'app_barang/barang/barang_list.html', {'barang': barang})
    else:
        return HttpResponse('Maaf barang tidak dapat dihapus karena telah digunakan oleh PO atau sebagai induk barang lain')
    
def barang_detail(request, pk):
    barang = get_object_or_404(Barang, pk=pk)
    
    po_terkait = PO.objects.filter(kode_barang=barang)

    anak_barang = Barang.objects.filter(induk=barang.kode)

    return render(request, 'app_barang/barang/barang_detail.html', {
        'barang': barang,
        'po_terkait': po_terkait,
        'anak_barang': anak_barang,
    })

def get_induk_barang(request):
    try:
        level = int(request.GET.get('level', 0))
        tipe = request.GET.get('tipe')
    except (ValueError, TypeError):
        return JsonResponse({'data': []})

    if tipe == 'G' and level > 1 or tipe == 'D':
        barang_list = Barang.objects.filter(level=level - 1, tipe='G')
    else:
        return JsonResponse({'data': []})  # Induk tidak diperlukan

    data = [{'id': b.id, 'kode': b.kode} for b in barang_list]
    return JsonResponse({'data': data})

# PO (Purchase Order) 
def po_list(request):
    pos = PO.objects.all()
    po_dipakai = {
        p.id: TerimaBarang.objects.filter(nomor_po=p).exists()
        for p in pos
    }
    return render(request, 'app_barang/po/po_list.html', {
        'pos': pos,
        'po_dipakai': po_dipakai
    })

def po_create(request):
    if request.method == 'POST':
        form = POForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('po_list')
    else:
        form = POForm()
    return render(request, 'app_barang/po/po_form.html', {'form': form})

def po_update(request, pk):
    po = get_object_or_404(PO, pk=pk)
    if request.method == 'POST':
        form = POForm(request.POST, instance=po)
        if form.is_valid():
            form.save()
            return redirect('po_list')
    else:
        form = POForm(instance=po)
    return render(request, 'app_barang/po/po_form.html', {'form': form})

def po_delete(request, pk):
    po = get_object_or_404(PO, pk=pk)
    if request.method == 'POST':
        po.delete()
        return redirect('po_list')
    return render(request, 'app_barang/po/po_list.html', {'po': po})

def po_detail(request, pk):
    po = get_object_or_404(PO, pk=pk)
    terima_list = TerimaBarang.objects.filter(nomor_po=po)
    return render(request, 'app_barang/po/po_detail.html', {
        'po': po,
        'terima_list': terima_list,
    })

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

def terima_barang_detail(request, pk):
    terima = get_object_or_404(TerimaBarang, pk=pk)
    return render(request, 'app_barang/terima_barang/terima_barang_detail.html', {
        'terima': terima,
    })

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
    return render(request, 'app_barang/terima_barang/terima_barang_form.html', {'form': form, 'is_edit': False})

def terima_barang_update(request, pk):
    terima_barang = get_object_or_404(TerimaBarang, pk=pk)
    po_lama = terima_barang.nomor_po
    qty_terima_lama = terima_barang.qty_terima
    po_lama_id = terima_barang.nomor_po.pk

    if request.method == 'POST':
        form = TerimaBarangForm(request.POST, instance=terima_barang)
        if form.is_valid():
            terima_barang_baru = form.save(commit=False)
            po_baru = terima_barang_baru.nomor_po
            qty_terima_baru = terima_barang_baru.qty_terima

            # Simulasi perubahan qty_terima
            if po_baru == po_lama:
                total_qty_terima = po_baru.qty_terima - qty_terima_lama + qty_terima_baru
            else:
                total_qty_terima_po_lama = po_lama.qty_terima - qty_terima_lama
                total_qty_terima_po_baru = po_baru.qty_terima + qty_terima_baru

                if total_qty_terima_po_baru > po_baru.qty_po:
                    form.add_error('qty_terima', 'Qty terima melebihi jumlah PO baru.')
                    return render(request, 'app_barang/terima_barang/terima_barang_form.html', {'form': form})

                # Update PO lama
                po_lama.qty_terima = total_qty_terima_po_lama
                po_lama.save()

                # Update PO baru
                po_baru.qty_terima = total_qty_terima_po_baru
                po_baru.save()

                terima_barang_baru.save()
                return redirect('terima_barang_list')

            # Kalau PO-nya tidak berubah
            if total_qty_terima > po_baru.qty_po:
                form.add_error('qty_terima', 'Qty terima melebihi jumlah PO.')
            else:
                po_baru.qty_terima = total_qty_terima
                po_baru.save()
                terima_barang_baru.save()
                return redirect('terima_barang_list')
    else:
        form = TerimaBarangForm(instance=terima_barang)

    form.fields['nomor_po'].queryset = PO.objects.filter(
        models.Q(qty_terima__lt=models.F('qty_po')) | models.Q(pk=terima_barang.nomor_po.pk)
    )
    return render(request, 'app_barang/terima_barang/terima_barang_form.html', {'form': form, 'is_edit': True, 'qty_terima_lama': qty_terima_lama, 'po_lama_id': po_lama_id,})



def terima_barang_delete(request, pk):
    terima_barang = get_object_or_404(TerimaBarang, pk=pk)
    if request.method == 'POST':
        po = terima_barang.nomor_po
        total_qty_terima = po.qty_terima - terima_barang.qty_terima
        po.qty_terima = total_qty_terima
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
            'qty_po' : po.qty_po,
            'qty_terima': po.qty_terima
        }
        
        return JsonResponse({'data': [data]})
    except PO.DoesNotExist:
        return JsonResponse({'data': []})
