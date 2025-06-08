import streamlit as st
from datetime import datetime
import json

st.set_page_config(
    page_title="Menu del Giorno",
    page_icon="logo.png"
)


@st.cache_resource
def get_menu(day: str):
    # retrieve the menu from the json file
    with open('menu.json', 'r') as f:
        menu_file = json.load(f)

    menu = menu_file.get("default", {})

    # use the day to get the extra menu
    if day in menu_file:
        menu["speciale del giorno"] = menu_file[day]

    return menu


# sessione state to define the item selected
if "selected_item" not in st.session_state:
    st.session_state.selected_item = {}


def clear_selection() -> None:
    """
    Svuota la selezione corrente e ricarica la pagina.
    """
    st.session_state.selected_item = {}
    st.rerun()


def compute_total():
    total = sum(item['price'] * item['quantity']
                for item in st.session_state.selected_item.values())
    return total


# Funzione per aggiungere un elemento al carrello
def aggiungi_al_carrello(section, name, price):
    key = f"{section}-{name}"
    if key in st.session_state.selected_item:
        st.session_state.selected_item[key]['quantity'] += 1
    else:
        st.session_state.selected_item[key] = {
            "name": name,
            "price": price,
            "quantity": 1
        }


def resoconto() -> str:
    """
    Crea un resoconto del carrello raggruppato per sezione.

    Returns:
        str: Resoconto formattato in Markdown.
    """
    if not st.session_state.selected_item:
        return "_Nessun elemento selezionato._"

    # Raggruppa per sezione
    sezioni = {}
    for key, item in st.session_state.selected_item.items():
        section, _ = key.split("-", 1)
        if section not in sezioni:
            sezioni[section] = []
        sezioni[section].append(item)

    lines = []
    for section, items in sezioni.items():
        lines.append(f"### {section.capitalize()}\n")
        for item in items:
            lines.append(
                f"- {item['name']} `{item['quantity']}`: {item['price']*item['quantity']:.2f}€")
        lines.append("")  # Riga vuota tra sezioni

    return "\n".join(lines)


today = datetime.now().strftime("%d-%m-%Y")
menu = get_menu(today)

st.title(f"Totale - {compute_total():.2f}€")


with st.sidebar:
    st.title(f"Resoconto - {compute_total():.2f}€")
    st.markdown(resoconto())

    if st.session_state.selected_item:
        st.divider()
        if st.button("Svuota carrello", key="clear_cart", help="Svuota il carrello e inizia una nuova selezione", use_container_width=True):
            clear_selection()
        st.divider()

        # Pagamento e resto
        totale = compute_total()
        pagamento = st.number_input(
            "Pagamento in contanti (€)", min_value=0.0, step=0.5, format="%.2f")
        if pagamento > 0:
            resto = pagamento - totale
            if resto < 0:
                st.warning("Importo insufficiente.")
            else:
                st.success(f"Resto: {resto:.2f}€")


# Crea una tab per ogni sezione
tabs = st.tabs([section.capitalize() for section in menu.keys()])

for i, (section, items) in enumerate(menu.items()):
    with tabs[i]:
        for name, price in items.items():

            if st.button(f"{name.capitalize()} - **{price:.2f}€**", key=f"add_{section}_{name}_{price}", use_container_width=True, type="primary"):
                aggiungi_al_carrello(section, name, price)
                st.rerun()  # Aggiorna la pagina per mostrare la quantità aggiornata

st.divider()

if st.button("Svuota carrello", key="clear_cart_down", help="Svuota il carrello e inizia una nuova selezione", use_container_width=True):
    clear_selection()
