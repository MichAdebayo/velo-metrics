import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api import get_stats, get_performances, get_performances_by_username
import requests

def show_statistics():
    st.title("Statistiques globales")

    if not st.session_state.is_staff:
        st.warning("Vous n'avez pas les droits d'administrateur nécessaires pour voir les statistiques globales.")
        return

    if stats := get_stats():
        st.subheader("Meilleurs athlètes")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Athlète le plus fort", stats.get('strongest_athlete', "Non disponible"))

        with col2:
            st.metric("Meilleur VO2max", stats.get('highest_vo2max', "Non disponible"))

        with col3:
            st.metric("Meilleur ratio puissance/poids", stats.get('best_power_weight_ratio', "Non disponible"))

        API_URL = "http://127.0.0.1:8000"
        headers = {"Authorization": f"Bearer {st.session_state.token}"}

        try:
            response = requests.get(f"{API_URL}/performances/all_users", headers=headers)
            if response.status_code == 200:
                all_users = response.json()
                user_names = [user.get('user_name', f"User {user.get('id')}") for user in all_users]
                user_ids = [user.get('id') for user in all_users]
                name_to_id = {user.get('user_name'): user.get('id') for user in all_users}
            else:
                user_names = []
                user_ids = list(range(1, 10))
                name_to_id = {}
        except Exception:
            user_names = []
            user_ids = list(range(1, 10))
            name_to_id = {}

        st.subheader("Comparaison des performances")
        st.info("Veuillez sélectionner des athlètes à comparer")

        comparison_type = st.radio("Sélectionner par", ["ID", "Nom"])

        if comparison_type == "ID":
            athlete_ids = st.multiselect(
                "Sélectionner des athlètes à comparer (par ID)", 
                options=user_ids or list(range(1, 10))
            )

            if athlete_ids:
                show_performance_comparison(athlete_ids)
        else:
            athlete_names = st.multiselect(
                "Sélectionner des athlètes à comparer (par nom)", 
                options=user_names or ["User 1", "User 2", "User 3"]
            )

            if athlete_names:

                athlete_ids = []
                for name in athlete_names:
                    if name in name_to_id:
                        athlete_ids.append(name_to_id[name])
                    else:

                        perfs = get_performances_by_username(name)
                        if perfs and len(perfs) > 0:

                            athlete_ids.append(perfs[0].get('user_id'))

                if athlete_ids:
                    show_performance_comparison(athlete_ids)
                else:
                    st.warning("Impossible de trouver des IDs pour les athlètes sélectionnés.")
    else:
        st.info("Aucune statistique disponible pour le moment.")

def show_performance_comparison(athlete_ids, name_to_id=None):
    performance_data = []

    for aid in athlete_ids:
        if perfs := get_performances(aid):
            avg_power = sum(p.get('power', 0) for p in perfs) / len(perfs) if perfs else 0

            athlete_name = f"Utilisateur #{aid}"
            if name_to_id:

                id_to_name = {v: k for k, v in name_to_id.items()}
                if aid in id_to_name:
                    athlete_name = id_to_name[aid]

            performance_data.append({
                'athlete_id': aid,
                'athlete_name': athlete_name,
                'avg_power': avg_power,
                'max_power': max(p.get('power', 0) for p in perfs) if perfs else 0,
                'avg_vo2max': sum(p.get('vo2_max', 0) for p in perfs) / len(perfs) if perfs else 0,
                'num_performances': len(perfs)
            })

    if performance_data:
        perf_df = pd.DataFrame(performance_data)

        fig1 = px.bar(
            perf_df, 
            x='athlete_name', 
            y=['avg_power', 'max_power'],
            barmode='group',
            title="Comparaison de la puissance par athlète"
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(
            perf_df, 
            x='athlete_name', 
            y='avg_vo2max',
            title="Comparaison du VO2max moyen par athlète"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aucune donnée de performance disponible.")