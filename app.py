import hashlib
import io
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, date
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

DB_PATH = "laundromat_app.db"
PACIFIC = ZoneInfo("America/Los_Angeles")

st.set_page_config(page_title="EZ Coin Laundry", page_icon="🧺", layout="centered")

st.markdown(
    """
    <style>
    /* Dedicated iPhone/mobile layout pass */
    .block-container {
        padding-top: 0.65rem;
        padding-left: 0.55rem;
        padding-right: 0.55rem;
        padding-bottom: 5rem;
        max-width: 720px;
    }
    h1 { font-size: 1.55rem !important; line-height: 1.2 !important; margin-bottom: .45rem !important; }
    h2 { font-size: 1.30rem !important; line-height: 1.2 !important; }
    h3 { font-size: 1.10rem !important; line-height: 1.2 !important; }
    p, label, div, span { font-size: 1rem; }
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    .stDownloadButton > button {
        width: 100%;
        min-height: 3.35rem;
        border-radius: 0.95rem;
        font-size: 1.02rem;
        font-weight: 700;
        margin-bottom: .25rem;
        white-space: normal;
    }
    div[data-testid="stMetric"] {
        background: rgba(250,250,250,0.06);
        padding: 0.8rem;
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 1rem;
        margin-bottom: .45rem;
    }
    div[data-testid="stMetricValue"] { font-size: 1.35rem !important; }
    .ez-card {
        padding: 0.9rem;
        border: 1px solid rgba(128,128,128,0.28);
        border-radius: 1rem;
        margin: 0.55rem 0 0.8rem 0;
        background: rgba(128,128,128,0.045);
    }
    .ez-card-title { font-weight: 800; font-size: 1.08rem; margin-bottom: .15rem; }
    .ez-card-line { opacity: .9; margin: .12rem 0; }
    .ez-pill {
        display: inline-block;
        padding: .25rem .55rem;
        border-radius: 999px;
        border: 1px solid rgba(128,128,128,.25);
        font-size: .88rem;
        margin-top: .2rem;
    }
    .qty-box {
        text-align:center;
        min-height: 3.25rem;
        padding:0.72rem 0;
        font-size:1.35rem;
        border:1px solid rgba(128,128,128,.35);
        border-radius:.95rem;
        background: rgba(250,250,250,.04);
    }
    .small-caption { font-size:0.88rem; opacity:0.78; }
    div[data-testid="stDataFrame"] { margin-top: .35rem; }
    div[data-testid="stHorizontalBlock"] { gap: 0.45rem; }
    @media (max-width: 700px) {
        .block-container { padding-left: 0.42rem; padding-right: 0.42rem; max-width: 100%; }
        h1 { font-size: 1.42rem !important; }
        h2 { font-size: 1.18rem !important; }
        h3 { font-size: 1.04rem !important; }
        div[data-testid="stHorizontalBlock"] { gap: 0.25rem; }
        div[data-testid="stButton"] > button,
        div[data-testid="stFormSubmitButton"] > button,
        .stDownloadButton > button { min-height: 3.55rem; font-size: 1.0rem; }
        .qty-box { min-height: 3.35rem; font-size: 1.45rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

TEXT = {
    "en": {
        "app_title": "EZ Coin Laundry",
        "login_english": "Login English",
        "login_spanish": "Login Spanish",
        "username": "Username",
        "password": "Password",
        "sign_in": "Sign In",
        "biometric": "Use Face ID / Biometric",
        "logout": "Logout",
        "main_menu": "Main Menu",
        "sales": "Sales",
        "customer_count": "Customer Count",
        "change_given": "Change Given",
        "bathroom": "Bathroom",
        "close_day": "Close Day",
        "daily_overview": "Daily Overview",
        "purchases_refunds": "Purchases & Refunds",
        "reports": "Reports",
        "admin": "Admin",
        "product": "Product",
        "done": "Done",
        "save": "Save",
        "back": "Back",
        "cancel": "Cancel",
        "sale_summary": "Sale Summary",
        "confirm_save_sale": "Confirm / Save Sale",
        "back_to_edit": "Back to Edit",
        "cancel_sale": "Cancel Sale",
        "sale_saved": "Sale saved",
        "total_collected": "Total collected",
        "total_to_collect": "Total to Collect",
        "products_sold_today": "Products Sold Today",
        "customer_count_entries": "Customer Count Entries",
        "change_given_entries": "Change Given Entries",
        "bathroom_entries": "Bathroom Entries",
        "summary": "Summary",
        "product_sales": "Product Sales",
        "products_sold_count": "Products Sold",
        "bathroom_sales": "Bathroom Sales",
        "total_sales": "Total Sales",
        "purchases": "Purchases",
        "refunds": "Refunds",
        "starting_cash": "Starting Cash",
        "money_on_hand": "Money on Hand",
        "expected_money_on_hand": "Expected Money on Hand",
        "over_short": "Over / Short",
        "notes": "Notes",
        "confirm_close_day": "Confirm Close Day",
        "add_adjustment": "Add Adjustment",
        "cash_coin_adjustments": "Cash / Coin Adjustments",
        "type": "Type",
        "purchase": "Purchase",
        "refund": "Refund",
        "category": "Category",
        "amount": "Amount",
        "description": "Description",
        "add_receipt": "Add receipt?",
        "yes": "Yes",
        "no": "No",
        "machine_number": "Machine Number",
        "customer_name": "Customer Name",
        "customer_phone": "Customer Phone",
        "issue_code": "Issue Code",
        "amount_refunded": "Amount Refunded",
        "issue_description": "Issue Description",
        "comment": "Comment",
        "inventory_received": "Inventory Received",
        "cases_received": "Cases Received",
        "units_per_case": "Units Per Case",
        "confirm_save_receipt": "Confirm / Save Receipt",
        "void": "Void",
        "open": "Open",
        "closed": "Closed",
        "recorded_by": "Recorded By",
        "timestamp": "Timestamp",
        "status": "Status",
        "qty": "Qty",
        "line_total": "Line Total",
        "unit_price": "Unit Price",
        "close_day_saved": "Day closed",
        "insufficient_permissions": "You do not have permission to access this page.",
        "day_closed": "This day is closed.",
        "enter_value": "Enter a value greater than zero.",
        "no_items_selected": "No items selected.",
        "entry_voided": "Entry voided.",
        "inventory_units": "Inventory Units",
        "display_order": "Display Order",
        "active": "Active",
        "role": "Role",
        "starting_rolled_coin_reserve": "Starting Rolled Coin Reserve",
        "reopen_day": "Reopen Day",
        "reopen_reason": "Reopen Reason",
        "day_reopened": "Day reopened",
        "return_to_menu": "Return to Menu",
        "today": "Date",
        "day_status": "Day Status",
        "language": "Language",
        "sales_home_help": "Tap Product to enter a transaction.",
        "products": "Products",
        "day": "Day",
        "export_excel": "Export to Excel",
        "cumulative_activity": "Cumulative Activity",
        "users": "Users",
        "settings": "Settings",
        "products_admin": "Products",
        "add_product": "Add Product",
        "add_user": "Add User",
        "update": "Update",
        "reopen_target_date": "Date to Reopen",
        "reopen_help": "Reopening keeps all line-item detail available and prevents double counting by replacing the close record for that date when closed again.",
        "transactions_today": "Transactions Today",
        "purchase_refund_history": "Purchases / Refunds Entered Today",
        "no_entries": "No entries yet.",
        "quantity": "Quantity",
        "save_entry": "Save Entry",
        "select_product": "Select Product",
        "daily_activity": "Daily Activity",
        "reopen_warning": "Only admins can reopen a closed day.",
        "select_business_day": "Select Business Day",
        "active_business_day": "Active Business Day",
        "closed_day_prompt": "This business day is closed. Reopen it before making changes.",
        "open_selected_day": "Open / Reopen Selected Day",
        "inventory_adjustments": "Inventory Adjustments",
        "inventory_position": "Inventory Position",
        "adjustment_type": "Adjustment Type",
        "quantity_change": "Quantity Change",
        "positive_or_negative": "Use positive numbers to add inventory and negative numbers to remove inventory.",
        "count_correction": "Count Correction",
        "damage_spoilage": "Damage / Spoilage",
        "theft_loss": "Theft / Loss",
        "found_inventory": "Found Inventory",
        "entry_correction": "Entry Correction",
        "other": "Other",
        "adjustment_saved": "Inventory adjustment saved",
        "business_date": "Business Date",
        "entered_at": "Entered At",
        "entered_by": "Entered By",
        "opening_inventory": "Opening Inventory",
        "received_units": "Received Units",
        "sold_units": "Sold Units",
        "adjusted_units": "Adjusted Units",
        "calculated_on_hand": "Calculated On Hand",
        "selected_day_help": "The app defaults to today, but you can select another business day for missed entries or corrections.",
    },
    "es": {
        "app_title": "EZ Coin Laundry",
        "login_english": "Iniciar en Inglés",
        "login_spanish": "Iniciar en Español",
        "username": "Usuario",
        "password": "Contraseña",
        "sign_in": "Ingresar",
        "biometric": "Usar Face ID / Biométrico",
        "logout": "Cerrar sesión",
        "main_menu": "Menú Principal",
        "sales": "Ventas",
        "customer_count": "Conteo de Clientes",
        "change_given": "Cambio Entregado",
        "bathroom": "Baño",
        "close_day": "Cerrar Día",
        "daily_overview": "Resumen Diario",
        "purchases_refunds": "Compras y Reembolsos",
        "reports": "Reportes",
        "admin": "Admin",
        "product": "Producto",
        "done": "Hecho",
        "save": "Guardar",
        "back": "Regresar",
        "cancel": "Cancelar",
        "sale_summary": "Resumen de Venta",
        "confirm_save_sale": "Confirmar / Guardar Venta",
        "back_to_edit": "Regresar a Editar",
        "cancel_sale": "Cancelar Venta",
        "sale_saved": "Venta guardada",
        "total_collected": "Total cobrado",
        "total_to_collect": "Total a Cobrar",
        "products_sold_today": "Productos Vendidos Hoy",
        "customer_count_entries": "Entradas de Conteo de Clientes",
        "change_given_entries": "Entradas de Cambio Entregado",
        "bathroom_entries": "Entradas de Baño",
        "summary": "Resumen",
        "product_sales": "Ventas de Productos",
        "products_sold_count": "Productos Vendidos",
        "bathroom_sales": "Ventas de Baño",
        "total_sales": "Ventas Totales",
        "purchases": "Compras",
        "refunds": "Reembolsos",
        "starting_cash": "Efectivo Inicial",
        "money_on_hand": "Dinero en Mano",
        "expected_money_on_hand": "Dinero Esperado en Mano",
        "over_short": "Sobrante / Faltante",
        "notes": "Notas",
        "confirm_close_day": "Confirmar Cierre del Día",
        "add_adjustment": "Agregar Ajuste",
        "cash_coin_adjustments": "Ajustes de Efectivo / Moneda",
        "type": "Tipo",
        "purchase": "Compra",
        "refund": "Reembolso",
        "category": "Categoría",
        "amount": "Monto",
        "description": "Descripción",
        "add_receipt": "¿Agregar recibo?",
        "yes": "Sí",
        "no": "No",
        "machine_number": "Número de Máquina",
        "customer_name": "Nombre del Cliente",
        "customer_phone": "Teléfono del Cliente",
        "issue_code": "Código de Problema",
        "amount_refunded": "Monto Reembolsado",
        "issue_description": "Descripción del Problema",
        "comment": "Comentario",
        "inventory_received": "Inventario Recibido",
        "cases_received": "Cajas Recibidas",
        "units_per_case": "Unidades por Caja",
        "confirm_save_receipt": "Confirmar / Guardar Recibo",
        "void": "Anular",
        "open": "Abierto",
        "closed": "Cerrado",
        "recorded_by": "Registrado Por",
        "timestamp": "Marca de Tiempo",
        "status": "Estado",
        "qty": "Cant.",
        "line_total": "Total de Línea",
        "unit_price": "Precio Unitario",
        "close_day_saved": "Día cerrado",
        "insufficient_permissions": "No tiene permiso para acceder a esta página.",
        "day_closed": "Este día está cerrado.",
        "enter_value": "Ingrese un valor mayor que cero.",
        "no_items_selected": "No hay productos seleccionados.",
        "entry_voided": "Entrada anulada.",
        "inventory_units": "Unidades de Inventario",
        "display_order": "Orden de Pantalla",
        "active": "Activo",
        "role": "Rol",
        "starting_rolled_coin_reserve": "Reserva Inicial de Moneda Enrollada",
        "reopen_day": "Reabrir Día",
        "reopen_reason": "Razón para Reabrir",
        "day_reopened": "Día reabierto",
        "return_to_menu": "Volver al Menú",
        "today": "Fecha",
        "day_status": "Estado del Día",
        "language": "Idioma",
        "sales_home_help": "Toque Producto para ingresar una transacción.",
        "products": "Productos",
        "day": "Día",
        "export_excel": "Exportar a Excel",
        "cumulative_activity": "Actividad Acumulada",
        "users": "Usuarios",
        "settings": "Configuración",
        "products_admin": "Productos",
        "add_product": "Agregar Producto",
        "add_user": "Agregar Usuario",
        "update": "Actualizar",
        "reopen_target_date": "Fecha a Reabrir",
        "reopen_help": "Reabrir mantiene disponible todo el detalle y evita doble conteo al reemplazar el cierre de esa fecha cuando se vuelva a cerrar.",
        "transactions_today": "Transacciones de Hoy",
        "purchase_refund_history": "Compras / Reembolsos Ingresados Hoy",
        "no_entries": "No hay entradas todavía.",
        "quantity": "Cantidad",
        "save_entry": "Guardar Entrada",
        "select_product": "Seleccione Producto",
        "daily_activity": "Actividad Diaria",
        "reopen_warning": "Solo administradores pueden reabrir un día cerrado.",
        "select_business_day": "Seleccionar Día de Trabajo",
        "active_business_day": "Día de Trabajo Activo",
        "closed_day_prompt": "Este día de trabajo está cerrado. Reábralo antes de hacer cambios.",
        "open_selected_day": "Abrir / Reabrir Día Seleccionado",
        "inventory_adjustments": "Ajustes de Inventario",
        "inventory_position": "Posición de Inventario",
        "adjustment_type": "Tipo de Ajuste",
        "quantity_change": "Cambio de Cantidad",
        "positive_or_negative": "Use números positivos para agregar inventario y negativos para quitar inventario.",
        "count_correction": "Corrección de Conteo",
        "damage_spoilage": "Daño / Merma",
        "theft_loss": "Robo / Pérdida",
        "found_inventory": "Inventario Encontrado",
        "entry_correction": "Corrección de Entrada",
        "other": "Otro",
        "adjustment_saved": "Ajuste de inventario guardado",
        "business_date": "Fecha de Trabajo",
        "entered_at": "Ingresado En",
        "entered_by": "Ingresado Por",
        "opening_inventory": "Inventario Inicial",
        "received_units": "Unidades Recibidas",
        "sold_units": "Unidades Vendidas",
        "adjusted_units": "Unidades Ajustadas",
        "calculated_on_hand": "Existencia Calculada",
        "selected_day_help": "La aplicación usa el día actual por defecto, pero puede seleccionar otro día de trabajo para entradas faltantes o correcciones.",
    },
}

PRODUCTS = [
    ("P001", "Tide polvo", 2.50, 1), ("P002", "Roma", 2.50, 2), ("P003", "Ariel", 2.50, 3),
    ("P004", "Tide 10oz", 2.50, 4), ("P005", "Gain 10oz", 2.50, 5), ("P006", "Tide Grande", 7.50, 6),
    ("P007", "Gain Grande", 7.50, 7), ("P008", "Tide 24", 6.50, 8), ("P009", "Awesome", 2.50, 9),
    ("P010", "Suavitel Sheet", 2.50, 10), ("P011", "Gain Sheet", 2.50, 11), ("P012", "Downey Grande", 4.00, 12),
    ("P013", "Downey Intense", 2.50, 13), ("P014", "Suavitel azul", 2.50, 14), ("P015", "Suavitel Sol", 2.50, 15),
    ("P016", "Clorox", 2.50, 16), ("P017", "Soillove", 2.50, 17), ("P018", "Bag", 1.00, 18),
    ("P019", "Soda", 1.50, 19), ("P020", "Water", 1.25, 20),
]
PURCHASE_CATEGORIES = ["Toilet paper", "Bleach", "Cleaning supplies", "Clean rags", "Other"]
REFUND_ISSUES = ["Too many clothes", "Too much soap", "Drained too quickly", "Did not spin", "Not enough water"]
ADJUSTMENT_TYPES = ["Cash Added", "Cash Taken", "Coin Added", "Coin Taken"]
INVENTORY_ADJUSTMENT_TYPES = ["Count Correction", "Damage / Spoilage", "Theft / Loss", "Found Inventory", "Entry Correction", "Other"]


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def now_pacific() -> datetime:
    return datetime.now(PACIFIC)


def now_iso() -> str:
    return now_pacific().isoformat(timespec="seconds")


def today_iso() -> str:
    return now_pacific().date().isoformat()


def t(key: str) -> str:
    return TEXT[st.session_state.get("lang", "en")].get(key, key)


def current_user() -> str:
    return st.session_state.get("user", "")


def current_role() -> str:
    return st.session_state.get("role", "")


def fmt_ts(value: str) -> str:
    try:
        return datetime.fromisoformat(value).astimezone(PACIFIC).strftime("%Y-%m-%d %I:%M %p")
    except Exception:
        return value or ""


def clear_data_cache():
    try:
        st.cache_data.clear()
    except Exception:
        pass


def init_db():
    with closing(get_conn()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                biometric_enabled INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_sale_price REAL NOT NULL,
                units_per_case INTEGER,
                starting_inventory_units INTEGER,
                active INTEGER NOT NULL DEFAULT 1,
                display_order INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sales_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                unit_price REAL NOT NULL,
                qty INTEGER NOT NULL,
                line_total REAL NOT NULL,
                entered_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                voided_by TEXT,
                voided_timestamp TEXT,
                void_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS customer_count_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                count_added INTEGER NOT NULL,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                voided_by TEXT,
                voided_timestamp TEXT,
                void_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS bathroom_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                bathroom_count INTEGER NOT NULL,
                sales_amount REAL NOT NULL,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                voided_by TEXT,
                voided_timestamp TEXT,
                void_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS change_given_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                amount REAL NOT NULL,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                voided_by TEXT,
                voided_timestamp TEXT,
                void_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS purchase_refund_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                category TEXT,
                amount REAL,
                description TEXT,
                receipt_image_name TEXT,
                receipt_image_bytes BLOB,
                machine_number INTEGER,
                customer_name TEXT,
                customer_phone TEXT,
                issue_code TEXT,
                issue_description TEXT,
                comment TEXT,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                voided_by TEXT,
                voided_timestamp TEXT,
                void_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS inventory_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                units_per_case INTEGER,
                cases_received INTEGER NOT NULL,
                units_added INTEGER NOT NULL,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved'
            );
            CREATE TABLE IF NOT EXISTS inventory_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_id TEXT NOT NULL,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                qty_change INTEGER NOT NULL,
                adjustment_type TEXT NOT NULL,
                notes TEXT,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                voided_by TEXT,
                voided_timestamp TEXT,
                void_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS cash_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                adjustment_type TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                recorded_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved'
            );
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS day_close (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                closed_timestamp TEXT NOT NULL,
                closed_by TEXT NOT NULL,
                product_sales REAL NOT NULL,
                bathroom_sales REAL NOT NULL,
                total_sales REAL NOT NULL,
                products_sold_count INTEGER NOT NULL DEFAULT 0,
                customer_count INTEGER NOT NULL,
                change_given REAL NOT NULL,
                purchases REAL NOT NULL,
                refunds REAL NOT NULL,
                starting_cash REAL NOT NULL,
                money_on_hand REAL NOT NULL,
                expected_money_on_hand REAL NOT NULL,
                over_short REAL NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Closed'
            );
            CREATE TABLE IF NOT EXISTS day_reopen_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_date TEXT NOT NULL,
                reopened_timestamp TEXT NOT NULL,
                reopened_by TEXT NOT NULL,
                reason TEXT
            );
            """
        )
        # Lightweight migrations for older local DBs.
        migrations = {
            "purchase_refund_entries": [
                ("comment", "TEXT"), ("voided_by", "TEXT"), ("voided_timestamp", "TEXT"), ("void_reason", "TEXT")
            ],
            "day_close": [("products_sold_count", "INTEGER NOT NULL DEFAULT 0")],
            "inventory_adjustments": [("voided_by", "TEXT"), ("voided_timestamp", "TEXT"), ("void_reason", "TEXT")],
        }
        for table, cols in migrations.items():
            existing = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
            for col, decl in cols:
                if col not in existing:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")

        if conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"] == 0:
            conn.executemany(
                "INSERT INTO users (username, password_hash, role, biometric_enabled) VALUES (?, ?, ?, ?)",
                [("admin", hash_password("admin123"), "admin", 1), ("editor", hash_password("editor123"), "editor", 0), ("viewer", hash_password("viewer123"), "viewer", 0)],
            )
        if conn.execute("SELECT COUNT(*) c FROM products").fetchone()["c"] == 0:
            conn.executemany(
                """
                INSERT INTO products (product_id, product_name, category, unit_sale_price, units_per_case,
                                      starting_inventory_units, active, display_order)
                VALUES (?, ?, 'Product', ?, 1, 0, 1, ?)
                """,
                [(pid, name, price, order) for pid, name, price, order in PRODUCTS],
            )
        for key, value in {"starting_cash_default": "0", "starting_rolled_coin_reserve": "0"}.items():
            if not conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone():
                conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()


@st.cache_data(ttl=20, show_spinner=False)
def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    with closing(get_conn()) as conn:
        return pd.read_sql_query(sql, conn, params=params)


@st.cache_data(ttl=30, show_spinner=False)
def fetch_products_df(active_only: bool = True) -> pd.DataFrame:
    sql = "SELECT * FROM products"
    if active_only:
        sql += " WHERE active = 1"
    sql += " ORDER BY display_order, product_name"
    return query_df(sql)


def execute(sql: str, params: tuple = ()):
    with closing(get_conn()) as conn:
        conn.execute(sql, params)
        conn.commit()
    clear_data_cache()


def executemany(sql: str, params):
    with closing(get_conn()) as conn:
        conn.executemany(sql, params)
        conn.commit()
    clear_data_cache()


def get_setting(key: str, default: str = "0") -> str:
    df = query_df("SELECT value FROM settings WHERE key = ?", (key,))
    return str(df.iloc[0]["value"]) if not df.empty else default


def set_setting(key: str, value: str):
    execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))


def business_date() -> str:
    return st.session_state.get("business_date", today_iso())


def get_day_status(day_str: str) -> str:
    df = query_df("SELECT status FROM day_close WHERE business_date = ? ORDER BY id DESC LIMIT 1", (day_str,))
    return str(df.iloc[0]["status"]) if not df.empty else "Open"


def is_day_closed(day_str: str) -> bool:
    return get_day_status(day_str) == "Closed"


def reopen_business_day(day_str: str, reason: str = ""):
    execute("UPDATE day_close SET status = 'Reopened' WHERE business_date = ? AND status = 'Closed'", (day_str,))
    execute("INSERT INTO day_reopen_log (business_date, reopened_timestamp, reopened_by, reason) VALUES (?, ?, ?, ?)", (day_str, now_iso(), current_user(), reason))


def render_closed_day_prompt():
    st.warning(t("closed_day_prompt"))
    if current_role() == "admin":
        with st.form(f"reopen_inline_{business_date()}"):
            reason = st.text_area(t("reopen_reason"), key=f"inline_reason_{business_date()}")
            reopen = st.form_submit_button(t("open_selected_day"), use_container_width=True)
        if reopen:
            reopen_business_day(business_date(), reason)
            st.success(t("day_reopened"))
            st.rerun()
    else:
        st.info(t("reopen_warning"))
    return_to_menu_button()
    st.stop()


def require_role(*roles: str):
    if current_role() not in roles:
        st.error(t("insufficient_permissions"))
        st.stop()


def guard_open_day():
    if is_day_closed(business_date()):
        render_closed_day_prompt()


def require_editor_or_admin_open_day():
    require_role("admin", "editor")
    guard_open_day()


@st.cache_data(ttl=10, show_spinner=False)
def summary_totals(day_str: str) -> dict:
    with closing(get_conn()) as conn:
        def scalar(sql, params=(day_str,)):
            return conn.execute(sql, params).fetchone()[0]
        product_sales = float(scalar("SELECT COALESCE(SUM(line_total),0) FROM sales_lines WHERE business_date = ? AND status != 'Void'"))
        products_sold_count = int(scalar("SELECT COALESCE(SUM(qty),0) FROM sales_lines WHERE business_date = ? AND status != 'Void'"))
        bathroom_sales = float(scalar("SELECT COALESCE(SUM(sales_amount),0) FROM bathroom_entries WHERE business_date = ? AND status != 'Void'"))
        bathroom_count = int(scalar("SELECT COALESCE(SUM(bathroom_count),0) FROM bathroom_entries WHERE business_date = ? AND status != 'Void'"))
        customer_count = int(scalar("SELECT COALESCE(SUM(count_added),0) FROM customer_count_entries WHERE business_date = ? AND status != 'Void'"))
        change_given = float(scalar("SELECT COALESCE(SUM(amount),0) FROM change_given_entries WHERE business_date = ? AND status != 'Void'"))
        purchases = float(scalar("SELECT COALESCE(SUM(amount),0) FROM purchase_refund_entries WHERE business_date = ? AND entry_type = 'Purchase' AND status != 'Void'"))
        refunds = float(scalar("SELECT COALESCE(SUM(amount),0) FROM purchase_refund_entries WHERE business_date = ? AND entry_type = 'Refund' AND status != 'Void'"))
        adjustments = float(scalar(
            """
            SELECT COALESCE(SUM(CASE
                WHEN adjustment_type IN ('Cash Added','Coin Added') THEN amount
                WHEN adjustment_type IN ('Cash Taken','Coin Taken') THEN -amount
                ELSE 0 END),0)
            FROM cash_adjustments WHERE business_date = ? AND status != 'Void'
            """
        ))
    return {
        "product_sales": round(product_sales, 2),
        "products_sold_count": products_sold_count,
        "bathroom_sales": round(bathroom_sales, 2),
        "bathroom_count": bathroom_count,
        "total_sales": round(product_sales + bathroom_sales, 2),
        "customer_count": customer_count,
        "change_given": round(change_given, 2),
        "purchases": round(purchases, 2),
        "refunds": round(refunds, 2),
        "net_adjustments": round(adjustments, 2),
    }



@st.cache_data(ttl=15, show_spinner=False)
def inventory_position_df() -> pd.DataFrame:
    return query_df(
        """
        WITH received AS (
            SELECT product_id, COALESCE(SUM(units_added),0) AS received_units
            FROM inventory_receipts
            WHERE status != 'Void'
            GROUP BY product_id
        ),
        sold AS (
            SELECT product_id, COALESCE(SUM(qty),0) AS sold_units
            FROM sales_lines
            WHERE status != 'Void'
            GROUP BY product_id
        ),
        adjusted AS (
            SELECT product_id, COALESCE(SUM(qty_change),0) AS adjusted_units
            FROM inventory_adjustments
            WHERE status != 'Void'
            GROUP BY product_id
        )
        SELECT p.product_id AS Product_ID,
               p.product_name AS Product,
               COALESCE(p.starting_inventory_units,0) AS Opening_Inventory,
               COALESCE(r.received_units,0) AS Received_Units,
               COALESCE(s.sold_units,0) AS Sold_Units,
               COALESCE(a.adjusted_units,0) AS Adjusted_Units,
               COALESCE(p.starting_inventory_units,0) + COALESCE(r.received_units,0) - COALESCE(s.sold_units,0) + COALESCE(a.adjusted_units,0) AS Calculated_On_Hand
        FROM products p
        LEFT JOIN received r ON r.product_id = p.product_id
        LEFT JOIN sold s ON s.product_id = p.product_id
        LEFT JOIN adjusted a ON a.product_id = p.product_id
        ORDER BY p.display_order, p.product_name
        """
    )

def get_carry_forward_starting_cash(day_str: str) -> float:
    df = query_df("SELECT money_on_hand FROM day_close WHERE business_date < ? AND status = 'Closed' ORDER BY business_date DESC, id DESC LIMIT 1", (day_str,))
    if not df.empty:
        return float(df.iloc[0]["money_on_hand"])
    return float(get_setting("starting_cash_default", "0"))


def ensure_state():
    st.session_state.setdefault("lang", "en")
    st.session_state.setdefault("page", "login")
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("business_date", today_iso())
    st.session_state.setdefault("cart", {})


def change_lang(lang_code: str):
    st.session_state.lang = lang_code


def render_login():
    st.title(t("app_title"))
    st.caption("Laundry sales, inventory, and close-day tracking")
    st.markdown("### Language / Idioma")
    lang_choice = st.radio("", ["English", "Español"], horizontal=True, index=1 if st.session_state.get("lang", "en") == "es" else 0, label_visibility="collapsed")
    desired = "es" if lang_choice == "Español" else "en"
    if desired != st.session_state.get("lang", "en"):
        change_lang(desired)
        st.rerun()
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        submitted = st.form_submit_button(t("sign_in"), use_container_width=True)
    if submitted:
        df = query_df("SELECT * FROM users WHERE username = ? AND active = 1", (username.strip(),))
        if not df.empty and str(df.iloc[0]["password_hash"]) == hash_password(password):
            st.session_state.authenticated = True
            st.session_state.user = str(df.iloc[0]["username"])
            st.session_state.role = str(df.iloc[0]["role"])
            st.session_state.page = "main_menu"
            st.rerun()
        st.error("Invalid login")
    st.button(t("biometric"), disabled=True, use_container_width=True)
    st.caption("Default demo logins: admin/admin123, editor/editor123, viewer/viewer123")

def render_global_header():
    with st.container():
        selected = st.date_input(
            t("select_business_day"),
            value=date.fromisoformat(business_date()),
            help=t("selected_day_help"),
            key="business_date_picker",
        )
        selected_iso = selected.isoformat()
        if selected_iso != business_date():
            st.session_state.business_date = selected_iso
            st.session_state.cart = {}
            st.rerun()
        status_label = t("closed") if is_day_closed(business_date()) else t("open")
        render_card(
            f"{t('active_business_day')}: {business_date()}",
            [f"<b>{t('day_status')}:</b> {status_label}", f"<b>{t('recorded_by')}:</b> {current_user()}"],
        )
        lang_choice = st.radio(t("language"), ["English", "Español"], horizontal=True, index=1 if st.session_state.get("lang", "en") == "es" else 0, key="language_toggle")
        desired = "es" if lang_choice == "Español" else "en"
        if desired != st.session_state.get("lang", "en"):
            change_lang(desired)
            st.rerun()
        c1, c2 = st.columns(2)
        if c1.button(t("main_menu"), use_container_width=True, key=f"header_menu_{st.session_state.page}"):
            st.session_state.page = "main_menu"
            st.rerun()
        if c2.button(t("logout"), use_container_width=True, key=f"header_logout_{st.session_state.page}"):
            lang = st.session_state.get("lang", "en")
            st.session_state.clear()
            ensure_state()
            st.session_state.lang = lang
            st.rerun()

def return_to_menu_button():
    if st.button(t("return_to_menu"), use_container_width=True, key=f"return_{st.session_state.page}"):
        st.session_state.page = "main_menu"
        st.rerun()


def nav_button(label, page, disabled=False):
    if st.button(label, use_container_width=True, disabled=disabled):
        st.session_state.page = page
        st.rerun()


def mobile_metric_grid(items):
    """Render metric cards in a narrow-friendly two-column rhythm."""
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for j, (label, value) in enumerate(items[i:i + 2]):
            cols[j].metric(label, value)


def render_card(title, lines=None, pill=None):
    line_html = "".join(f"<div class='ez-card-line'>{line}</div>" for line in (lines or []))
    pill_html = f"<div class='ez-pill'>{pill}</div>" if pill else ""
    st.markdown(
        f"<div class='ez-card'><div class='ez-card-title'>{title}</div>{line_html}{pill_html}</div>",
        unsafe_allow_html=True,
    )


def compact_table_cards(df: pd.DataFrame, title_col: str | None = None, max_rows: int = 8):
    """Show a phone-readable card preview before the full scrollable table."""
    if df.empty:
        st.info(t("no_entries"))
        return
    for _, row in df.head(max_rows).iterrows():
        title = str(row[title_col]) if title_col and title_col in df.columns else str(row.iloc[0])
        lines = []
        for col in df.columns:
            if col == title_col:
                continue
            val = row[col]
            if pd.isna(val):
                continue
            lines.append(f"<b>{col}:</b> {val}")
        render_card(title, lines[:6])
    if len(df) > max_rows:
        st.caption(f"Showing latest {max_rows} of {len(df)} records. Full table below.")
    with st.expander("Full table"):
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_main_menu():
    st.title(t("main_menu"))
    render_global_header()
    totals = summary_totals(business_date())
    mobile_metric_grid([
        (t("total_sales"), f"${totals['total_sales']:.2f}"),
        (t("customer_count"), totals["customer_count"]),
        (t("products_sold_count"), totals["products_sold_count"]),
        (t("bathroom"), totals["bathroom_count"]),
    ])
    st.markdown("### Actions")
    pages = [(t("sales"), "sales_home", current_role() not in {"admin", "editor"}),
             (t("customer_count"), "customer_count", current_role() not in {"admin", "editor"}),
             (t("change_given"), "change_given", current_role() not in {"admin", "editor"}),
             (t("bathroom"), "bathroom", current_role() not in {"admin", "editor"}),
             (t("purchases_refunds"), "purchases_refunds", current_role() not in {"admin", "editor"}),
             (t("daily_overview"), "daily_overview", False),
             (t("close_day"), "close_day", current_role() not in {"admin", "editor"}),
             (t("reports"), "reports", current_role() not in {"admin", "viewer"}),
             (t("admin"), "admin", current_role() != "admin"),
             (t("inventory_received"), "inventory_received", current_role() != "admin"),
             (t("inventory_adjustments"), "inventory_adjustments", current_role() != "admin")]
    for label, page, disabled in pages:
        nav_button(label, page, disabled)

def render_sales_home():
    require_role("admin", "editor")
    st.title(t("sales"))
    render_global_header()
    if msg := st.session_state.pop("flash_message", None):
        st.success(msg)
    st.caption(t("sales_home_help"))
    if st.button(t("product"), use_container_width=True):
        st.session_state.cart = {}
        st.session_state.page = "product_entry"
        st.rerun()
    return_to_menu_button()


def render_product_entry():
    require_editor_or_admin_open_day()
    st.title(t("product"))
    render_global_header()
    cart = st.session_state.setdefault("cart", {})
    products = fetch_products_df(True)
    if products.empty:
        st.warning(t("no_entries"))
        return
    for _, product in products.iterrows():
        pid = str(product["product_id"])
        qty = int(cart.get(pid, 0))
        st.markdown(f"<div class='ez-card-title'>{product['product_name']}</div><div class='small-caption'>${float(product['unit_sale_price']):.2f}</div>", unsafe_allow_html=True)
        cols = st.columns([1, 1.15, 1])
        if cols[0].button("−", key=f"minus_{pid}", use_container_width=True):
            cart[pid] = max(0, qty - 1)
            st.session_state.cart = cart
            st.rerun()
        cols[1].markdown(f"<div class='qty-box'><b>{int(cart.get(pid, 0))}</b></div>", unsafe_allow_html=True)
        if cols[2].button("+", key=f"plus_{pid}", use_container_width=True):
            cart[pid] = qty + 1
            st.session_state.cart = cart
            st.rerun()
        st.markdown("---")
    total_items = sum(int(v) for v in cart.values())
    st.subheader(f"{t('products_sold_count')}: {total_items}")
    if st.button(t("done"), use_container_width=True):
        if not any(v > 0 for v in cart.values()):
            st.warning(t("no_items_selected"))
        else:
            st.session_state.page = "sale_summary"
            st.rerun()
    return_to_menu_button()

def render_sale_summary():
    require_editor_or_admin_open_day()
    st.title(t("sale_summary"))
    render_global_header()
    cart = st.session_state.get("cart", {})
    products = fetch_products_df(False).set_index("product_id")
    rows, total = [], 0.0
    for pid, qty in cart.items():
        if int(qty) > 0 and pid in products.index:
            product = products.loc[pid]
            line_total = float(product["unit_sale_price"]) * int(qty)
            rows.append({"Product": product["product_name"], t("qty"): int(qty), t("unit_price"): round(float(product["unit_sale_price"]), 2), t("line_total"): round(line_total, 2)})
            total += line_total
    if rows:
        compact_table_cards(pd.DataFrame(rows), title_col="Product", max_rows=20)
    else:
        st.warning(t("no_items_selected"))
    st.subheader(f"{t('total_to_collect')}: ${total:.2f}")
    with st.form("sale_summary_form"):
        save = st.form_submit_button(t("confirm_save_sale"), use_container_width=True)
        edit = st.form_submit_button(t("back_to_edit"), use_container_width=True)
        cancel = st.form_submit_button(t("cancel_sale"), use_container_width=True)
    if save:
        txid, ts = str(uuid.uuid4()), now_iso()
        params = []
        for pid, qty in cart.items():
            if int(qty) > 0 and pid in products.index:
                p = products.loc[pid]
                params.append((txid, business_date(), ts, pid, p["product_name"], float(p["unit_sale_price"]), int(qty), round(float(p["unit_sale_price"]) * int(qty), 2), current_user()))
        if params:
            executemany(
                """
                INSERT INTO sales_lines (transaction_id, business_date, timestamp, product_id, product_name, unit_price, qty, line_total, entered_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Saved')
                """,
                params,
            )
            clear_data_cache()
            st.session_state.cart = {}
            st.session_state.flash_message = f"{t('sale_saved')} | {t('total_collected')}: ${total:.2f}"
            st.session_state.page = "sales_home"
            st.rerun()
    if edit:
        st.session_state.page = "product_entry"
        st.rerun()
    if cancel:
        st.session_state.cart = {}
        st.session_state.page = "sales_home"
        st.rerun()

def render_counter_page(page_key: str, label: str, save_fn, step: int = 1, currency: bool = False):
    require_editor_or_admin_open_day()
    st.title(label)
    render_global_header()
    state_key = f"counter_{page_key}"
    st.session_state.setdefault(state_key, 0)
    cols = st.columns([1, 1.2, 1])
    if cols[0].button("−" if not currency else f"−${step}", use_container_width=True):
        st.session_state[state_key] = max(0, int(st.session_state[state_key]) - step)
        st.rerun()
    cols[1].markdown(f"<div class='qty-box'><b>{'$' if currency else ''}{st.session_state[state_key]}</b></div>", unsafe_allow_html=True)
    if cols[2].button("+" if not currency else f"+${step}", use_container_width=True):
        st.session_state[state_key] = int(st.session_state[state_key]) + step
        st.rerun()
    with st.form(f"{page_key}_form"):
        note = st.text_input(t("notes"), key=f"{page_key}_note")
        submitted = st.form_submit_button(t("save_entry"), use_container_width=True)
    if submitted:
        value = int(st.session_state[state_key])
        if value <= 0:
            st.warning(t("enter_value"))
        else:
            save_fn(value, note)
            st.session_state[state_key] = 0
            st.session_state.page = "main_menu"
            st.rerun()
    return_to_menu_button()

def save_customer_count(count: int, note: str = ""):
    execute("INSERT INTO customer_count_entries (business_date, timestamp, count_added, recorded_by, status) VALUES (?, ?, ?, ?, 'Saved')", (business_date(), now_iso(), count, current_user()))


def save_bathroom(count: int, note: str = ""):
    execute("INSERT INTO bathroom_entries (business_date, timestamp, bathroom_count, sales_amount, recorded_by, status) VALUES (?, ?, ?, ?, ?, 'Saved')", (business_date(), now_iso(), count, float(count), current_user()))


def save_change_given(amount: int, note: str = ""):
    execute("INSERT INTO change_given_entries (business_date, timestamp, amount, recorded_by, status) VALUES (?, ?, ?, ?, 'Saved')", (business_date(), now_iso(), float(amount), current_user()))


def purchase_refund_rows(day_str: str) -> pd.DataFrame:
    return query_df(
        """
        SELECT id, timestamp, entry_type, category, amount, description, machine_number, customer_name,
               customer_phone, issue_code, issue_description, comment, recorded_by, status
        FROM purchase_refund_entries
        WHERE business_date = ?
        ORDER BY id DESC
        """,
        (day_str,),
    )


def render_purchases_refunds():
    require_editor_or_admin_open_day()
    st.title(t("purchases_refunds"))
    render_global_header()
    entry_type = st.radio(t("type"), [t("purchase"), t("refund")], horizontal=True)
    with st.form("purchase_refund_form", clear_on_submit=True):
        receipt_name, receipt_bytes = None, None
        if entry_type == t("purchase"):
            category = st.selectbox(t("category"), PURCHASE_CATEGORIES)
            description = st.text_input(t("description")) if category == "Other" else ""
            amount = st.number_input(t("amount"), min_value=0.0, format="%.2f")
            add_receipt = st.checkbox(t("add_receipt"))
            receipt = st.file_uploader("Receipt photo", type=["png", "jpg", "jpeg"], disabled=not add_receipt)
            if receipt is not None:
                receipt_name, receipt_bytes = receipt.name, receipt.read()
            machine_number = customer_name = customer_phone = issue_code = issue_description = comment = None
            real_entry_type = "Purchase"
        else:
            category = "Refund"
            amount = st.number_input(t("amount_refunded"), min_value=0.0, format="%.2f")
            machine_number = st.number_input(t("machine_number"), min_value=0, step=1)
            customer_name = st.text_input(t("customer_name"))
            customer_phone = st.text_input(t("customer_phone"))
            issue_code = st.text_input(t("issue_code"))
            issue_description = st.selectbox(t("issue_description"), REFUND_ISSUES)
            comment = st.text_area(t("comment"))
            description = ""
            real_entry_type = "Refund"
        submitted = st.form_submit_button(t("save"), use_container_width=True)
    if submitted:
        if amount <= 0:
            st.warning(t("enter_value"))
        else:
            with closing(get_conn()) as conn:
                conn.execute(
                    """
                    INSERT INTO purchase_refund_entries
                    (business_date, timestamp, entry_type, category, amount, description, receipt_image_name, receipt_image_bytes,
                     machine_number, customer_name, customer_phone, issue_code, issue_description, comment, recorded_by, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Saved')
                    """,
                    (business_date(), now_iso(), real_entry_type, category, float(amount), description, receipt_name, receipt_bytes,
                     int(machine_number) if machine_number not in (None, "") else None, customer_name, customer_phone, issue_code, issue_description, comment, current_user()),
                )
                conn.commit()
            clear_data_cache()
            st.success(t("save"))
            st.rerun()
    st.markdown(f"### {t('purchase_refund_history')}")
    df = purchase_refund_rows(business_date())
    if not df.empty:
        df["timestamp"] = df["timestamp"].apply(fmt_ts)
    compact_table_cards(df, title_col="entry_type", max_rows=8)
    return_to_menu_button()


def render_daily_overview():
    st.title(t("daily_overview"))
    render_global_header()
    totals = summary_totals(business_date())
    mobile_metric_grid([
        (t("product_sales"), f"${totals['product_sales']:.2f}"),
        (t("products_sold_count"), totals["products_sold_count"]),
        (t("bathroom"), totals["bathroom_count"]),
        (t("total_sales"), f"${totals['total_sales']:.2f}"),
        (t("customer_count"), totals["customer_count"]),
        (t("change_given"), f"${totals['change_given']:.2f}"),
        (t("purchases"), f"${totals['purchases']:.2f}"),
        (t("refunds"), f"${totals['refunds']:.2f}"),
    ])
    overview = pd.DataFrame([{
        "Date": business_date(),
        "Day of the Week": pd.to_datetime(business_date()).day_name(),
        "Product Sales ($)": totals["product_sales"],
        "Products Sold": totals["products_sold_count"],
        "Bathroom": totals["bathroom_count"],
        "Total Sales ($)": totals["total_sales"],
        "Customer Count": totals["customer_count"],
        "Change Given": totals["change_given"],
        "Purchases ($)": totals["purchases"],
        "Refunds ($)": totals["refunds"],
    }])
    with st.expander("Full daily summary table"):
        st.dataframe(overview, use_container_width=True, hide_index=True)
    st.markdown(f"### {t('products_sold_today')}")
    sales = query_df("SELECT timestamp, product_name, unit_price, qty, line_total, entered_by, status FROM sales_lines WHERE business_date = ? ORDER BY id DESC", (business_date(),))
    if not sales.empty:
        sales["timestamp"] = sales["timestamp"].apply(fmt_ts)
    compact_table_cards(sales, title_col="product_name")
    st.markdown(f"### {t('customer_count_entries')}")
    show_event_table("customer_count_entries", "count_added")
    st.markdown(f"### {t('bathroom_entries')}")
    show_event_table("bathroom_entries", "bathroom_count")
    st.markdown(f"### {t('change_given_entries')}")
    show_event_table("change_given_entries", "amount")
    st.markdown(f"### {t('purchase_refund_history')}")
    df = purchase_refund_rows(business_date())
    if not df.empty:
        df["timestamp"] = df["timestamp"].apply(fmt_ts)
    compact_table_cards(df, title_col="entry_type")
    st.markdown(f"### {t('inventory_position')}")
    pos = inventory_position_df()
    compact_table_cards(pos, title_col="Product", max_rows=6)
    return_to_menu_button()

def show_event_table(table: str, value_col: str):
    df = query_df(f"SELECT timestamp, {value_col}, recorded_by, status FROM {table} WHERE business_date = ? ORDER BY id DESC", (business_date(),))
    if not df.empty:
        df["timestamp"] = df["timestamp"].apply(fmt_ts)
    compact_table_cards(df, title_col=value_col, max_rows=5)

def render_close_day():
    require_role("admin", "editor")
    st.title(t("close_day"))
    render_global_header()
    if is_day_closed(business_date()):
        render_closed_day_prompt()
        return
    totals = summary_totals(business_date())
    mobile_metric_grid([
        (t("product_sales"), f"${totals['product_sales']:.2f}"),
        (t("bathroom_sales"), f"${totals['bathroom_sales']:.2f}"),
        (t("purchases"), f"${totals['purchases']:.2f}"),
        (t("refunds"), f"${totals['refunds']:.2f}"),
    ])
    st.markdown(f"### {t('cash_coin_adjustments')}")
    adj_df = query_df("SELECT timestamp, adjustment_type, amount, note, recorded_by, status FROM cash_adjustments WHERE business_date = ? ORDER BY id DESC", (business_date(),))
    if not adj_df.empty:
        adj_df["timestamp"] = adj_df["timestamp"].apply(fmt_ts)
    compact_table_cards(adj_df, title_col="adjustment_type", max_rows=5)
    with st.expander(t("add_adjustment")):
        with st.form("adjustment_form", clear_on_submit=True):
            adjustment_type = st.selectbox("Adjustment Type", ADJUSTMENT_TYPES)
            amount = st.number_input(t("amount"), min_value=0.0, format="%.2f")
            note = st.text_input(t("notes"))
            submitted = st.form_submit_button(t("save"), use_container_width=True)
        if submitted:
            execute("INSERT INTO cash_adjustments (business_date, timestamp, adjustment_type, amount, note, recorded_by, status) VALUES (?, ?, ?, ?, ?, ?, 'Saved')", (business_date(), now_iso(), adjustment_type, float(amount), note, current_user()))
            st.rerun()
    starting_cash_default = get_carry_forward_starting_cash(business_date())
    with st.form("close_day_form"):
        starting_cash = st.number_input(t("starting_cash"), min_value=0.0, value=float(starting_cash_default), format="%.2f")
        money_on_hand = st.number_input(t("money_on_hand"), min_value=0.0, format="%.2f")
        expected_money_on_hand = starting_cash + totals["total_sales"] - totals["change_given"] - totals["refunds"] - totals["purchases"] + totals["net_adjustments"]
        over_short = money_on_hand - expected_money_on_hand
        render_card(t("summary"), [f"<b>{t('expected_money_on_hand')}:</b> ${expected_money_on_hand:.2f}", f"<b>{t('over_short')}:</b> ${over_short:.2f}"])
        notes = st.text_area(t("notes"))
        confirm = st.form_submit_button(t("confirm_close_day"), use_container_width=True)
    if confirm:
        execute("UPDATE day_close SET status = 'Replaced' WHERE business_date = ? AND status = 'Closed'", (business_date(),))
        execute(
            """
            INSERT INTO day_close (business_date, closed_timestamp, closed_by, product_sales, bathroom_sales, total_sales,
                                   products_sold_count, customer_count, change_given, purchases, refunds, starting_cash,
                                   money_on_hand, expected_money_on_hand, over_short, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Closed')
            """,
            (business_date(), now_iso(), current_user(), totals["product_sales"], totals["bathroom_sales"], totals["total_sales"],
             totals["products_sold_count"], totals["customer_count"], totals["change_given"], totals["purchases"], totals["refunds"],
             float(starting_cash), float(money_on_hand), float(expected_money_on_hand), float(over_short), notes),
        )
        st.success(t("close_day_saved"))
        st.session_state.page = "main_menu"
        st.rerun()
    return_to_menu_button()

def render_inventory_received():
    require_role("admin")
    st.title(t("inventory_received"))
    render_global_header()
    guard_open_day()
    products = fetch_products_df(True)
    if products.empty:
        st.info(t("no_entries"))
        return
    with st.form("inventory_received_form"):
        selected = st.selectbox(t("select_product"), [f"{r.product_name} | {r.product_id}" for r in products.itertuples()])
        pid = selected.split(" | ")[-1]
        product = products[products["product_id"] == pid].iloc[0]
        units_per_case = st.number_input(t("units_per_case"), min_value=1, step=1, value=int(product["units_per_case"] or 1))
        cases_received = st.number_input(t("cases_received"), min_value=0, step=1)
        submitted = st.form_submit_button(t("confirm_save_receipt"), use_container_width=True)
    if submitted:
        if cases_received <= 0:
            st.warning(t("enter_value"))
        else:
            units_added = int(units_per_case) * int(cases_received)
            receipt_id = str(uuid.uuid4())
            execute("INSERT INTO inventory_receipts (receipt_id, business_date, timestamp, product_id, product_name, units_per_case, cases_received, units_added, recorded_by, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Saved')", (receipt_id, business_date(), now_iso(), pid, product["product_name"], int(units_per_case), int(cases_received), units_added, current_user()))
            execute("UPDATE products SET units_per_case = ? WHERE product_id = ?", (int(units_per_case), pid))
            st.success(f"{units_added} units added")
            st.rerun()
    df = query_df("SELECT business_date, timestamp, product_name, units_per_case, cases_received, units_added, recorded_by FROM inventory_receipts WHERE business_date = ? ORDER BY id DESC LIMIT 50", (business_date(),))
    if not df.empty:
        df["timestamp"] = df["timestamp"].apply(fmt_ts)
    compact_table_cards(df, title_col="product_name", max_rows=8)
    return_to_menu_button()



def render_inventory_adjustments():
    require_role("admin")
    st.title(t("inventory_adjustments"))
    render_global_header()
    guard_open_day()
    products = fetch_products_df(True)
    if products.empty:
        st.info(t("no_entries"))
        return_to_menu_button()
        return

    with st.form("inventory_adjustment_form", clear_on_submit=True):
        selected = st.selectbox(t("select_product"), [f"{r.product_name} | {r.product_id}" for r in products.itertuples()])
        pid = selected.split(" | ")[-1]
        product = products[products["product_id"] == pid].iloc[0]
        adjustment_type = st.selectbox(t("adjustment_type"), INVENTORY_ADJUSTMENT_TYPES)
        qty_change = st.number_input(t("quantity_change"), step=1, value=0, help=t("positive_or_negative"))
        notes = st.text_area(t("notes"))
        submitted = st.form_submit_button(t("save"), use_container_width=True)
    if submitted:
        if int(qty_change) == 0:
            st.warning(t("enter_value"))
        else:
            execute(
                """
                INSERT INTO inventory_adjustments
                (adjustment_id, business_date, timestamp, product_id, product_name, qty_change, adjustment_type, notes, recorded_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Saved')
                """,
                (str(uuid.uuid4()), business_date(), now_iso(), pid, product["product_name"], int(qty_change), adjustment_type, notes, current_user()),
            )
            st.success(t("adjustment_saved"))
            st.rerun()

    st.markdown(f"### {t('inventory_position')}")
    pos = inventory_position_df()
    compact_table_cards(pos, title_col="Product", max_rows=6)

    st.markdown(f"### {t('inventory_adjustments')}")
    df = query_df(
        """
        SELECT business_date, timestamp, product_name, qty_change, adjustment_type, notes, recorded_by, status
        FROM inventory_adjustments
        WHERE business_date = ?
        ORDER BY id DESC
        """,
        (business_date(),),
    )
    if not df.empty:
        df["timestamp"] = df["timestamp"].apply(fmt_ts)
    compact_table_cards(df, title_col="product_name", max_rows=8)
    return_to_menu_button()

def cumulative_activity_df() -> pd.DataFrame:
    return query_df(
        """
        SELECT business_date AS Date,
               closed_timestamp AS Closed_Timestamp,
               closed_by AS Closed_By,
               product_sales AS Product_Sales,
               products_sold_count AS Products_Sold,
               bathroom_sales AS Bathroom_Sales,
               total_sales AS Total_Sales,
               customer_count AS Customer_Count,
               change_given AS Change_Given,
               purchases AS Purchases,
               refunds AS Refunds,
               starting_cash AS Starting_Cash,
               money_on_hand AS Money_On_Hand,
               expected_money_on_hand AS Expected_Money_On_Hand,
               over_short AS Over_Short,
               notes AS Notes
        FROM day_close
        WHERE status = 'Closed'
        ORDER BY business_date DESC, id DESC
        """
    )


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cumulative Activity")
    return output.getvalue()


def render_reports():
    require_role("admin", "viewer")
    st.title(t("reports"))
    render_global_header()
    df = cumulative_activity_df()
    st.markdown(f"### {t('cumulative_activity')}")
    if df.empty:
        st.info(t("no_entries"))
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(t("export_excel"), data=df_to_excel_bytes(df), file_name="EZ_Coin_Laundry_Cumulative_Activity.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    return_to_menu_button()


def render_admin():
    require_role("admin")
    st.title(t("admin"))
    render_global_header()
    tab1, tab2, tab3, tab4 = st.tabs([t("reopen_day"), t("products_admin"), t("users"), t("settings")])
    with tab1:
        st.info(t("reopen_help"))
        with st.form("reopen_form"):
            reopen_date = st.date_input(t("reopen_target_date"), value=date.fromisoformat(business_date()))
            reason = st.text_area(t("reopen_reason"))
            submitted = st.form_submit_button(t("reopen_day"), use_container_width=True)
        if submitted:
            ds = reopen_date.isoformat()
            reopen_business_day(ds, reason)
            st.session_state.business_date = ds
            st.success(t("day_reopened"))
            st.rerun()
    with tab2:
        products = fetch_products_df(False)
        st.dataframe(products, use_container_width=True, hide_index=True)
        with st.form("product_admin_form"):
            st.markdown(f"#### {t('add_product')} / {t('update')}")
            product_id = st.text_input("Product ID", value=f"P{len(products)+1:03d}")
            product_name = st.text_input("Product Name")
            price = st.number_input(t("unit_price"), min_value=0.0, format="%.2f")
            units_per_case = st.number_input(t("units_per_case"), min_value=1, step=1, value=1)
            display_order = st.number_input(t("display_order"), min_value=1, step=1, value=int(len(products)+1))
            active = st.checkbox(t("active"), value=True)
            submitted = st.form_submit_button(t("save"), use_container_width=True)
        if submitted and product_id and product_name:
            execute("""
                INSERT INTO products (product_id, product_name, category, unit_sale_price, units_per_case, starting_inventory_units, active, display_order)
                VALUES (?, ?, 'Product', ?, ?, 0, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET product_name=excluded.product_name, unit_sale_price=excluded.unit_sale_price,
                    units_per_case=excluded.units_per_case, active=excluded.active, display_order=excluded.display_order
            """, (product_id.strip(), product_name.strip(), float(price), int(units_per_case), 1 if active else 0, int(display_order)))
            st.success(t("save"))
            st.rerun()
    with tab3:
        users = query_df("SELECT username, role, active, biometric_enabled FROM users ORDER BY username")
        st.dataframe(users, use_container_width=True, hide_index=True)
        with st.form("user_admin_form"):
            username = st.text_input(t("username"))
            password = st.text_input(t("password"), type="password")
            role = st.selectbox(t("role"), ["admin", "editor", "viewer"])
            active = st.checkbox(t("active"), value=True)
            submitted = st.form_submit_button(t("add_user"), use_container_width=True)
        if submitted and username and password:
            execute("""
                INSERT INTO users (username, password_hash, role, active) VALUES (?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash, role=excluded.role, active=excluded.active
            """, (username.strip(), hash_password(password), role, 1 if active else 0))
            st.success(t("save"))
            st.rerun()
    with tab4:
        with st.form("settings_form"):
            starting_cash_default = st.number_input(t("starting_cash"), min_value=0.0, value=float(get_setting("starting_cash_default", "0")), format="%.2f")
            starting_rolled_coin_reserve = st.number_input(t("starting_rolled_coin_reserve"), min_value=0.0, value=float(get_setting("starting_rolled_coin_reserve", "0")), format="%.2f")
            submitted = st.form_submit_button(t("update"), use_container_width=True)
        if submitted:
            set_setting("starting_cash_default", str(float(starting_cash_default)))
            set_setting("starting_rolled_coin_reserve", str(float(starting_rolled_coin_reserve)))
            st.success(t("save"))
            st.rerun()
    return_to_menu_button()


def render_page():
    if not st.session_state.get("authenticated", False):
        render_login()
        return
    page = st.session_state.get("page", "main_menu")
    if page == "main_menu": render_main_menu()
    elif page == "sales_home": render_sales_home()
    elif page == "product_entry": render_product_entry()
    elif page == "sale_summary": render_sale_summary()
    elif page == "customer_count": render_counter_page("customer_count", t("customer_count"), save_customer_count, step=1, currency=False)
    elif page == "bathroom": render_counter_page("bathroom", t("bathroom"), save_bathroom, step=1, currency=False)
    elif page == "change_given": render_counter_page("change_given", t("change_given"), save_change_given, step=5, currency=True)
    elif page == "purchases_refunds": render_purchases_refunds()
    elif page == "daily_overview": render_daily_overview()
    elif page == "close_day": render_close_day()
    elif page == "inventory_received": render_inventory_received()
    elif page == "inventory_adjustments": render_inventory_adjustments()
    elif page == "reports": render_reports()
    elif page == "admin": render_admin()
    else:
        st.session_state.page = "main_menu"
        st.rerun()


def main():
    init_db()
    ensure_state()
    render_page()


if __name__ == "__main__":
    main()
