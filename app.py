from flask import Flask, redirect, render_template, url_for, request
from peewee import *
import datetime, random

db = "penjualan.db"
database = SqliteDatabase(db)

class BaseModel(Model):
    class Meta:
        database=database

class Produk(BaseModel):
    id = AutoField(primary_key=True)
    nama_produk = CharField()
    harga_produk = IntegerField()
    stok_produk = IntegerField()

class Cart(BaseModel):
    id = AutoField(primary_key=True)
    id_produk = ForeignKeyField(Produk)
    jumlah_barang = IntegerField()


class Transaksi(BaseModel):
    id = AutoField(primary_key=True)
    id_transaksi = CharField() # iki ngkok isine iku random number misale : 47891412741
    id_produk = ForeignKeyField(Produk)
    jumlah_barang = IntegerField()
    tanggal_transaksi = DateTimeField()
    total_harga = IntegerField()


def create_tables():
    with database:
        database.create_tables([Produk,Cart, Transaksi])

app = Flask(__name__)

@app.route("/")
def index():
    selek_prodak = Produk.select()
    return render_template('index.html',data=selek_prodak)

@app.route('/tambah_produk', methods=['GET',"POST"])
def tambah_produk():
    if request.method == "GET":
        return render_template("tambah_produk.html")
    else:
        namaProduk = request.form['nama_produk']
        hargaProduk = request.form['harga_produk']
        stokProduk = request.form['stok_produk']

        Produk.create(nama_produk=namaProduk, 
            harga_produk=hargaProduk, 
            stok_produk = stokProduk
        )

        return redirect(url_for("index"))

@app.route('/update_produk/<id_produk>',methods=['GET','POST'])
def update_produk(id_produk):
    if request.method == 'GET':
        selek_prodak = Produk.select().where(Produk.id == id_produk)
        selek_prodak = selek_prodak.get()
        return render_template("update_produk.html",data=selek_prodak)
    else:
        namaProduk = request.form['nama_produk']
        hargaProduk = request.form['harga_produk']
        stokProduk = request.form['stok_produk']

        produkupdate = Produk.update(
            nama_produk=namaProduk,
            harga_produk=hargaProduk,
            stok_produk = stokProduk
        ).where(Produk.id == id_produk)
        
        produkupdate.execute()

        return redirect(url_for('index'))

@app.route('/delete_produk/<id_produk>')
def delete_produk(id_produk):
    deleteproduk = Produk.delete().where(Produk.id == id_produk)
    deleteproduk.execute()

    return redirect(url_for('index'))

@app.route('/cart')
def cartview():
    datacart = Cart.select()
    return render_template('cart.html',data=datacart)

@app.route('/add_to_cart/<id_produk>')
def addtocart(id_produk):
    cek_cart = Cart.select().where(Cart.id_produk == id_produk)
    if cek_cart.exists():
        isi_cart = cek_cart.get()
        edit_jumlah_beli = Cart.update(jumlah_barang= isi_cart.jumlah_barang+1).where(Cart.id_produk == id_produk)
        edit_jumlah_beli.execute()
        return redirect(url_for('cartview'))
    else:
        Cart.create(id_produk=id_produk,jumlah_barang=1)
        return redirect(url_for('cartview'))

@app.route('/edit_cart/<id_cart>',methods=['POST','GET'])
def edit_cart(id_cart):
    if request.method == 'GET':
        selek_cart = Cart.select().where(Cart.id == id_cart) #iki bentuke ngunu [] <= koyok ngunu
        selek_cart = selek_cart.get() # Lah iki ngunu bentuke {} <= ngene
        return render_template("edit_cart.html",data=selek_cart)
    else:
        jumlah_barang = request.form['jumlah_barang']

        update_cart = Cart.update(jumlah_barang=jumlah_barang).where(Cart.id == id_cart)
        
        update_cart.execute()

        return redirect(url_for('cartview'))

@app.route('/delete_cart/<id_cart>')
def delete_cart(id_cart):
    deletecart = Cart.delete().where(Cart.id == id_cart)
    deletecart.execute()

    return redirect(url_for('cartview'))

@app.route('/transaksi')
def transaksi():
    data = Transaksi.select()
    return render_template('transaksi.html', data=data)

@app.route('/create_transaksi')
def create_transaksi():

    id_transaksi = random.randint(100000,999999)
    tanggal_transaksi = datetime.datetime.now()
    # selek cart
    selek_cart = Cart.select()
    for i in selek_cart:
        id_produk = int(str(i.id_produk))
        jumlah_barang = i.jumlah_barang
        total_harga = jumlah_barang * i.id_produk.harga_produk

        # update stok produk
        Update_produk = Produk.update(stok_produk=i.id_produk.stok_produk-jumlah_barang).where(Produk.id == i.id_produk)
        Update_produk.execute()

        # create transaksi
        Transaksi.create(
            id_transaksi=id_transaksi,
            id_produk=id_produk,
            jumlah_barang=jumlah_barang,
            total_harga=total_harga,
            tanggal_transaksi=tanggal_transaksi
        )

    # delete cart
    Delete_cart = Cart.delete()
    Delete_cart.execute()

    return redirect(url_for('transaksi'))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)