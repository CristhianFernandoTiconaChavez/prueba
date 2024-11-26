import streamlit as st
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

# Función para resolver problemas de transporte
def solve_transportation(costs, supply, demand, capacities=None, route_minimums=None, prohibited_routes=None):
    num_origins = len(supply)
    num_destinations = len(demand)

    # Crear modelo
    prob = LpProblem("Transportation_Problem", LpMinimize)

    # Variables de decisión
    x = [[LpVariable(f"x_{i}_{j}", lowBound=0) for j in range(num_destinations)] for i in range(num_origins)]

    # Función objetivo
    prob += lpSum(costs[i][j] * x[i][j] for i in range(num_origins) for j in range(num_destinations))

    # Restricciones de oferta
    for i in range(num_origins):
        prob += lpSum(x[i][j] for j in range(num_destinations)) <= supply[i], f"Supply_{i}"

    # Restricciones de demanda
    for j in range(num_destinations):
        prob += lpSum(x[i][j] for i in range(num_origins)) >= demand[j], f"Demand_{j}"

    # Capacidades máximas
    if capacities:
        for i in range(num_origins):
            for j in range(num_destinations):
                prob += x[i][j] <= capacities[i][j], f"Capacity_{i}_{j}"

    # Mínimos por ruta
    if route_minimums:
        for i in range(num_origins):
            for j in range(num_destinations):
                prob += x[i][j] >= route_minimums[i][j], f"RouteMin_{i}_{j}"

    # Rutas prohibidas
    if prohibited_routes:
        for i, j in prohibited_routes:
            prob += x[i][j] == 0, f"Prohibited_{i}_{j}"

    # Resolver el problema
    prob.solve()

    # Resultados
    solution = {
        "status": LpStatus[prob.status],
        "total_cost": prob.objective.value(),
        "variables": {(i, j): x[i][j].varValue for i in range(num_origins) for j in range(num_destinations)}
    }
    return solution

# Interfaz en Streamlit
st.title("Problema de Transporte Interactivo")

# Configurar número de orígenes y destinos
st.sidebar.header("Definir el problema")
num_origins = st.sidebar.number_input("Número de orígenes", min_value=1, value=3)
num_destinations = st.sidebar.number_input("Número de destinos", min_value=1, value=3)

# Matriz de costos
st.subheader("Definir la matriz de costos")
costs = []
for i in range(num_origins):
    row = st.text_input(f"Costos desde origen {i+1} a cada destino (separados por comas)", value=",".join(["0"] * num_destinations))
    costs.append([float(x) for x in row.split(",")])

# Oferta
st.subheader("Definir la oferta")
supply = st.text_input("Oferta en cada origen (separados por comas)", value=",".join(["0"] * num_origins))
supply = [float(x) for x in supply.split(",")]

# Demanda
st.subheader("Definir la demanda")
demand = st.text_input("Demanda en cada destino (separados por comas)", value=",".join(["0"] * num_destinations))
demand = [float(x) for x in demand.split(",")]

# Opciones avanzadas
st.sidebar.subheader("Opciones avanzadas")
use_capacities = st.sidebar.checkbox("¿Usar restricciones de capacidad?")
use_route_minimums = st.sidebar.checkbox("¿Usar mínimos por ruta?")
use_prohibited_routes = st.sidebar.checkbox("¿Especificar rutas prohibidas?")

capacities, route_minimums, prohibited_routes = None, None, None

if use_capacities:
    st.subheader("Definir capacidades máximas")
    capacities = []
    for i in range(num_origins):
        row = st.text_input(f"Capacidades máximas desde origen {i+1} a cada destino (separados por comas)", value=",".join(["0"] * num_destinations))
        capacities.append([float(x) for x in row.split(",")])

if use_route_minimums:
    st.subheader("Definir mínimos por ruta")
    route_minimums = []
    for i in range(num_origins):
        row = st.text_input(f"Mínimos desde origen {i+1} a cada destino (separados por comas)", value=",".join(["0"] * num_destinations))
        route_minimums.append([float(x) for x in row.split(",")])

if use_prohibited_routes:
    st.subheader("Definir rutas prohibidas")
    prohibited_routes_input = st.text_area(
        "Rutas prohibidas (formato: i,j separados por comas, una por línea)",
        placeholder="Ejemplo:\n0,2\n1,1"
    )
    if prohibited_routes_input:
        prohibited_routes = [tuple(map(int, line.split(','))) for line in prohibited_routes_input.strip().split('\n')]

# Botón para resolver
if st.button("Resolver problema"):
    solution = solve_transportation(costs, supply, demand, capacities, route_minimums, prohibited_routes)

    st.subheader("Resultados")
    st.write(f"Estado: {solution['status']}")
    st.write(f"Costo total: {solution['total_cost']}")

    # Mostrar variables de decisión
    variables = [
        {"Origen": i+1, "Destino": j+1, "Unidades": solution["variables"][(i, j)]}
        for i in range(num_origins) for j in range(num_destinations)
    ]
    st.write(variables)

    # Descargar solución
    csv = "Origen,Destino,Unidades\n" + "\n".join([f"{v['Origen']},{v['Destino']},{v['Unidades']}" for v in variables])
    st.download_button("Descargar solución", data=csv, file_name="solucion_transporte.csv", mime="text/csv")
