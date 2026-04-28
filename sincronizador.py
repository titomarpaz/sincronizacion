import psycopg2

# Configuración de conexión (Local)
local_conn = psycopg2.connect("dbname=tu_base_local user=postgres password=tu_pass")

# Configuración de conexión (Supabase)
# Estos datos los sacas de Project Settings -> Database en Supabase
supa_conn = psycopg2.connect(
    host="db.xxxxxx.supabase.co",
    port="5432",
    dbname="postgres",
    user="postgres",
    password="tu_password_de_supabase"
)

def sincronizar_productos():
    with local_conn.cursor() as local_cur, supa_conn.cursor() as supa_cur:
        # 1. Leemos solo lo necesario de la laptop
        local_cur.execute("SELECT gtin, nombre, precio, stock FROM productos")
        productos = local_cur.fetchall()

        # 2. Subimos a Supabase (Upsert: Inserta o actualiza si ya existe)
        for p in productos:
            supa_cur.execute("""
                INSERT INTO productos_web (gtin, nombre, precio_venta, stock_disponible)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (gtin) DO UPDATE SET
                    nombre = EXCLUDED.nombre,
                    precio_venta = EXCLUDED.precio_venta,
                    stock_disponible = EXCLUDED.stock_disponible;
            """, p)
        
        supa_conn.commit()
        print("Sincronización exitosa.")

if __name__ == "__main__":
    sincronizar_productos()