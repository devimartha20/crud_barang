from django.urls import path
from . import views

urlpatterns = [
    path('pemasok/', views.pemasok_list, name='pemasok_list'),
    path('pemasok/update/<int:pk>/', views.pemasok_update, name='pemasok_update'),
    path('pemasok/delete/<int:pk>/', views.pemasok_delete, name='pemasok_delete'),

    path('gudang/', views.gudang_list, name='gudang_list'),
    path('gudang/update/<int:pk>/', views.gudang_update, name='gudang_update'),
    path('gudang/delete/<int:pk>/', views.gudang_delete, name='gudang_delete'),
    
    path('barang/', views.barang_list, name='barang_list'),
    path('barang/create/', views.barang_create, name='barang_create'),
    path('barang/update/<int:pk>/', views.barang_update, name='barang_update'),
    path('barang/delete/<int:pk>/', views.barang_delete, name='barang_delete'),
    path('get-induk-barang/', views.get_induk_barang, name='get_induk_barang'),

    path('po/', views.po_list, name='po_list'),
    path('po/create/', views.po_create, name='po_create'),
    path('po/update/<int:pk>/', views.po_update, name='po_update'),
    path('po/delete/<int:pk>/', views.po_delete, name='po_delete'),
    
    path('ajax/get-alamat/', views.get_gudang_alamat, name='get_alamat'),
    path('ajax/get-harga/', views.get_barang_harga, name='get_harga'),

    path('terima-barang/', views.terima_barang_list, name='terima_barang_list'),
    path('terima-barang/create/', views.terima_barang_create, name='terima_barang_create'),
    path('terima-barang/update/<int:pk>/', views.terima_barang_update, name='terima_barang_update'),
    path('terima-barang/delete/<int:pk>/', views.terima_barang_delete, name='terima_barang_delete'),
    path('get-barang-by-po/', views.get_barang_by_po, name='get_barang_by_po'),

    
    
]
