
import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Banker's Algorithm Simulator",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F7F9FC;
    }

    [data-testid="stSidebar"] {
        background-color: #EDF3FA;
    }

    .main-title {
        color: #17365D;
        font-size: 34px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 24px;
    }

    .section-title {
        color: #17365D;
        font-size: 25px;
        font-weight: 700;
        margin-top: 12px;
    }

    .safe-banner {
        background-color: #E8F5E9;
        border-left: 5px solid #23934B;
        padding: 17px;
        border-radius: 8px;
        color: #176B35;
        font-weight: 600;
    }

    .unsafe-banner {
        background-color: #FDECEC;
        border-left: 5px solid #D64545;
        padding: 17px;
        border-radius: 8px;
        color: #A52A2A;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 10px;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# STANDARD EXAMPLE
# =====================================================

STANDARD_AVAILABLE = [3, 3, 2]

STANDARD_ALLOCATION = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2]
]

STANDARD_MAXIMUM = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3]
]


# =====================================================
# BANKER'S ALGORITHM
# =====================================================

def calculate_need(maximum, allocation):

    need = []

    for i in range(len(maximum)):

        row = []

        for j in range(len(maximum[i])):

            value = maximum[i][j] - allocation[i][j]

            if value < 0:
                raise ValueError(
                    f"Allocation exceeds maximum demand for P{i}."
                )

            row.append(value)

        need.append(row)

    return need


def run_safety_algorithm(available, allocation, need):

    process_count = len(allocation)

    work = available.copy()
    finish = [False] * process_count

    safe_sequence = []
    execution_steps = []

    while len(safe_sequence) < process_count:

        found_process = False

        for i in range(process_count):

            if finish[i]:
                continue

            can_execute = all(
                need[i][j] <= work[j]
                for j in range(len(available))
            )

            if can_execute:

                before = work.copy()

                for j in range(len(available)):
                    work[j] += allocation[i][j]

                finish[i] = True
                safe_sequence.append(f"P{i}")

                execution_steps.append({
                    "Process": f"P{i}",
                    "Need": need[i].copy(),
                    "Before": before,
                    "Released": allocation[i].copy(),
                    "After": work.copy()
                })

                found_process = True
                break

        if not found_process:
            break

    return all(finish), safe_sequence, execution_steps


def check_resource_request(
    process,
    request,
    available,
    allocation,
    need
):

    for j in range(len(request)):

        if request[j] > need[process][j]:

            return (
                False,
                "Request exceeds the process's remaining maximum need.",
                []
            )

    for j in range(len(request)):

        if request[j] > available[j]:

            return (
                False,
                "Not enough resources are currently available.",
                []
            )

    new_available = available.copy()
    new_allocation = [row.copy() for row in allocation]
    new_need = [row.copy() for row in need]

    for j in range(len(request)):

        new_available[j] -= request[j]
        new_allocation[process][j] += request[j]
        new_need[process][j] -= request[j]

    is_safe, sequence, _ = run_safety_algorithm(
        new_available,
        new_allocation,
        new_need
    )

    if is_safe:

        return (
            True,
            "Request can be granted. The resulting system state is safe.",
            sequence
        )

    return (
        False,
        "Request denied because it would make the system unsafe.",
        sequence
    )


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_resource_names(count):

    return [
        f"Resource {chr(65 + i)}"
        for i in range(count)
    ]


def get_process_names(count):

    return [
        f"P{i}"
        for i in range(count)
    ]


def get_default_data(process_count, resource_count):

    if process_count == 5 and resource_count == 3:

        return (
            STANDARD_AVAILABLE.copy(),
            [row.copy() for row in STANDARD_ALLOCATION],
            [row.copy() for row in STANDARD_MAXIMUM]
        )

    available = [0] * resource_count

    allocation = [
        [0] * resource_count
        for _ in range(process_count)
    ]

    maximum = [
        [0] * resource_count
        for _ in range(process_count)
    ]

    return available, allocation, maximum


def convert_matrix(dataframe):

    result = []

    for row in dataframe.values:

        converted = []

        for value in row:

            number = float(value)

            if not number.is_integer() or number < 0:
                raise ValueError(
                    "Enter only non-negative whole numbers."
                )

            converted.append(int(number))

        result.append(converted)

    return result


def calculate_totals(
    allocation,
    available,
    process_count,
    resource_count
):

    allocated = [
        sum(allocation[i][j] for i in range(process_count))
        for j in range(resource_count)
    ]

    total = [
        allocated[j] + available[j]
        for j in range(resource_count)
    ]

    return allocated, total


def initialize_simulation():

    available, allocation, maximum = get_default_data(5, 3)

    need = calculate_need(maximum, allocation)

    safe, sequence, steps = run_safety_algorithm(
        available,
        allocation,
        need
    )

    return {
        "available": available,
        "allocation": allocation,
        "maximum": maximum,
        "need": need,
        "safe": safe,
        "sequence": sequence,
        "steps": steps,
        "process_count": 5,
        "resource_count": 3
    }


def reset_standard():

    st.session_state.simulation_data = initialize_simulation()
    st.session_state.request_result = None

    st.session_state.process_count_setting = 5
    st.session_state.resource_count_setting = 3

    for key in list(st.session_state.keys()):

        if key.startswith((
            "available_editor_",
            "allocation_editor_",
            "maximum_editor_",
            "request_value_"
        )):
            del st.session_state[key]


# =====================================================
# SESSION STATE
# =====================================================

if "simulation_data" not in st.session_state:
    st.session_state.simulation_data = initialize_simulation()

if "request_result" not in st.session_state:
    st.session_state.request_result = None


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown(
    "<h2 style='color:#17365D;'>💻 Banker's Simulator</h2>",
    unsafe_allow_html=True
)

st.sidebar.caption("OPERATING SYSTEMS PROJECT")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Resource Input",
        "Safety Analysis",
        "Resource Requests"
    ]
)

st.sidebar.markdown("---")

st.sidebar.subheader("Simulation Settings")

process_count = st.sidebar.number_input(
    "Number of processes",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
    key="process_count_setting"
)

resource_count = st.sidebar.number_input(
    "Number of resource types",
    min_value=1,
    max_value=5,
    value=3,
    step=1,
    key="resource_count_setting"
)

st.sidebar.info(
    "Start with the standard example "
    "(5 processes and 3 resource types), "
    "or change the counts to create your own scenario."
)

st.sidebar.button(
    "Reset to Standard Example",
    use_container_width=True,
    on_click=reset_standard
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Banker's Algorithm Simulator\n"
    "Deadlock Avoidance and Safe Resource Allocation"
)


# =====================================================
# CURRENT SIMULATION DATA
# =====================================================

data = st.session_state.simulation_data

available = data["available"]
allocation = data["allocation"]
maximum = data["maximum"]
need = data["need"]

current_process_count = data["process_count"]
current_resource_count = data["resource_count"]

resource_names = get_resource_names(current_resource_count)
process_names = get_process_names(current_process_count)

allocated_totals, total_resources = calculate_totals(
    allocation,
    available,
    current_process_count,
    current_resource_count
)


# =====================================================
# COMMON HEADER
# =====================================================

st.markdown(
    "<div class='main-title'>Banker's Algorithm Simulator</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Operating Systems | "
    "Deadlock Avoidance | Safe Resource Allocation</div>",
    unsafe_allow_html=True
)


# =====================================================
# PAGE 1: DASHBOARD
# =====================================================

if page == "Dashboard":

    st.markdown(
        "<div class='section-title'>System Dashboard</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Monitor system resources, process execution and system safety."
    )

    st.markdown("### System Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Processes", current_process_count)

    with c2:
        st.metric("Resource Types", current_resource_count)

    with c3:
        st.metric(
            "Completed Processes",
            len(data["sequence"])
        )

    with c4:
        st.metric(
            "System Status",
            "SAFE" if data["safe"] else "UNSAFE"
        )

    st.markdown("---")

    st.markdown("### Current System Status")

    if data["safe"]:

        st.markdown(
            "<div class='safe-banner'>"
            "✓ SYSTEM SAFE — All processes can complete safely."
            "</div>",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            "<div class='unsafe-banner'>"
            "✗ SYSTEM UNSAFE — A complete safe sequence was not found."
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("### Safe Execution Sequence")

    if data["safe"]:

        st.success(" → ".join(data["sequence"]))

    else:

        st.warning("No complete safe sequence exists.")

    st.markdown("---")

    st.markdown("### Total Resource Overview")

    overview = pd.DataFrame(
        {
            "Allocated": allocated_totals,
            "Available": available,
            "Total Resources": total_resources
        },
        index=resource_names
    )

    st.dataframe(
        overview,
        use_container_width=True
    )

    st.markdown("### Resource Distribution")

    chart_data = pd.DataFrame(
        {
            "Allocated": allocated_totals,
            "Available": available
        },
        index=resource_names
    )

    st.bar_chart(
        chart_data,
        use_container_width=True
    )

    st.info(
        "Use the sidebar to enter a new scenario, "
        "analyse system safety or test a resource request."
    )


# =====================================================
# PAGE 2: RESOURCE INPUT
# =====================================================

elif page == "Resource Input":

    st.markdown(
        "<div class='section-title'>Resource Input</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Enter the available resources, current allocation "
        "and maximum resource requirements."
    )

    if (
        current_process_count != process_count
        or current_resource_count != resource_count
    ):

        st.warning(
            "The sidebar settings have changed. "
            "Enter the matrices below and run the simulation "
            "to apply the new dimensions."
        )

        default_available, default_allocation, default_maximum = (
            get_default_data(process_count, resource_count)
        )

    else:

        default_available = available.copy()
        default_allocation = [row.copy() for row in allocation]
        default_maximum = [row.copy() for row in maximum]

    new_resource_names = get_resource_names(resource_count)
    new_process_names = get_process_names(process_count)

    editor_suffix = f"{process_count}_{resource_count}"

    with st.form("resource_input_form"):

        st.markdown("### Available Resources")

        available_df = pd.DataFrame(
            [default_available],
            columns=new_resource_names,
            index=["Available"]
        )

        available_df = st.data_editor(
            available_df,
            num_rows="fixed",
            use_container_width=True,
            key=f"available_editor_{editor_suffix}",
            column_config={
                name: st.column_config.NumberColumn(
                    name,
                    min_value=0,
                    step=1
                )
                for name in new_resource_names
            }
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### Allocation Matrix")

            allocation_df = pd.DataFrame(
                default_allocation,
                columns=new_resource_names,
                index=new_process_names
            )

            allocation_df = st.data_editor(
                allocation_df,
                num_rows="fixed",
                use_container_width=True,
                key=f"allocation_editor_{editor_suffix}",
                column_config={
                    name: st.column_config.NumberColumn(
                        name,
                        min_value=0,
                        step=1
                    )
                    for name in new_resource_names
                }
            )

        with col2:

            st.markdown("### Maximum Demand Matrix")

            maximum_df = pd.DataFrame(
                default_maximum,
                columns=new_resource_names,
                index=new_process_names
            )

            maximum_df = st.data_editor(
                maximum_df,
                num_rows="fixed",
                use_container_width=True,
                key=f"maximum_editor_{editor_suffix}",
                column_config={
                    name: st.column_config.NumberColumn(
                        name,
                        min_value=0,
                        step=1
                    )
                    for name in new_resource_names
                }
            )

        submitted = st.form_submit_button(
            "Run Safety Analysis",
            type="primary",
            use_container_width=True
        )

        if submitted:

            try:

                new_available = convert_matrix(available_df)[0]
                new_allocation = convert_matrix(allocation_df)
                new_maximum = convert_matrix(maximum_df)

                new_need = calculate_need(
                    new_maximum,
                    new_allocation
                )

                safe, sequence, steps = run_safety_algorithm(
                    new_available,
                    new_allocation,
                    new_need
                )

                st.session_state.simulation_data = {
                    "available": new_available,
                    "allocation": new_allocation,
                    "maximum": new_maximum,
                    "need": new_need,
                    "safe": safe,
                    "sequence": sequence,
                    "steps": steps,
                    "process_count": process_count,
                    "resource_count": resource_count
                }

                st.session_state.request_result = None

                st.success(
                    "Simulation updated successfully! "
                    "Open Safety Analysis to see the results."
                )

            except (ValueError, TypeError) as error:

                st.error(str(error))

            except Exception as error:

                st.error(f"Error: {error}")


# =====================================================
# PAGE 3: SAFETY ANALYSIS
# =====================================================

elif page == "Safety Analysis":

    st.markdown(
        "<div class='section-title'>Safety Analysis</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Examine the Need Matrix and determine whether "
        "the current system state is safe."
    )

    if data["safe"]:

        st.markdown(
            "<div class='safe-banner'>"
            "✓ SAFE STATE — A complete safe sequence exists."
            "</div>",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            "<div class='unsafe-banner'>"
            "✗ UNSAFE STATE — No complete safe sequence exists."
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("### Need Matrix")

    need_df = pd.DataFrame(
        need,
        columns=resource_names,
        index=process_names
    )

    st.dataframe(
        need_df,
        use_container_width=True
    )

    st.caption("Need = Maximum Demand − Allocation")

    st.markdown("---")

    st.markdown("### Safe Sequence")

    if data["safe"]:

        st.success(" → ".join(data["sequence"]))

    else:

        st.warning(
            "The system cannot find an execution order "
            "in which all processes complete."
        )

    st.markdown("---")

    st.markdown("### Step-by-Step Process Execution")

    st.write(
        "A process can execute when its remaining Need "
        "is less than or equal to the current Available resources."
    )

    if data["steps"]:

        for index, step in enumerate(data["steps"]):

            with st.expander(
                f"Step {index + 1}: {step['Process']}"
            ):

                st.write(f"**Need:** {step['Need']}")

                st.write(
                    f"**Available before:** {step['Before']}"
                )

                st.write(
                    f"**Resources released:** {step['Released']}"
                )

                st.write(
                    f"**Available after:** {step['After']}"
                )

                st.success(
                    f"{step['Process']} completed successfully."
                )

    else:

        st.warning("No process can execute in the current state.")

    st.markdown("---")

    st.markdown("### Process-wise Allocation")

    allocation_df = pd.DataFrame(
        allocation,
        columns=resource_names,
        index=process_names
    )

    st.bar_chart(
        allocation_df,
        use_container_width=True
    )

    st.markdown("### Maximum Demand Matrix")

    maximum_df = pd.DataFrame(
        maximum,
        columns=resource_names,
        index=process_names
    )

    st.dataframe(
        maximum_df,
        use_container_width=True
    )


# =====================================================
# PAGE 4: RESOURCE REQUESTS
# =====================================================

elif page == "Resource Requests":

    st.markdown(
        "<div class='section-title'>Resource Request Simulation</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Test whether an additional resource request "
        "can be safely granted to a process."
    )

    st.markdown("### Current Available Resources")

    available_overview = pd.DataFrame(
        [available],
        columns=resource_names,
        index=["Available"]
    )

    st.dataframe(
        available_overview,
        use_container_width=True
    )

    st.markdown("---")

    with st.form("request_form"):

        selected_process = st.selectbox(
            "Select requesting process",
            process_names
        )

        process_index = process_names.index(selected_process)

        st.write(
            f"Remaining Need for {selected_process}: "
            f"{need[process_index]}"
        )

        request_columns = st.columns(current_resource_count)

        request_values = []

        for j in range(current_resource_count):

            with request_columns[j]:

                value = st.number_input(
                    f"{resource_names[j]} request",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"request_value_{j}"
                )

                request_values.append(int(value))

        check = st.form_submit_button(
            "Check Resource Request",
            type="primary",
            use_container_width=True
        )

        if check:

            result = check_resource_request(
                process_index,
                request_values,
                available,
                allocation,
                need
            )

            st.session_state.request_result = result

    if st.session_state.request_result is not None:

        accepted, message, sequence = (
            st.session_state.request_result
        )

        st.markdown("---")

        st.markdown("### Request Result")

        if accepted:

            st.success("✓ " + message)

            st.write(
                "**Safe sequence after tentative allocation:**"
            )

            st.success(" → ".join(sequence))

        else:

            st.warning("⚠ " + message)

            if sequence:

                st.write(
                    "The tentative allocation did not produce "
                    "a complete safe sequence."
                )

    st.markdown("---")

    st.markdown("### Request Validation Rules")

    st.write("""
    1. Request must not exceed the process's remaining Need.
    2. Request must not exceed currently Available resources.
    3. The resulting state must remain safe after tentative allocation.
    """)

    st.info(
        "The simulator uses temporary allocation for checking. "
        "The original resource matrices are not permanently modified."
    )


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center; color:#64748B; padding:12px;'>
        Banker's Algorithm Simulator<br>
        Educational Project for Operating Systems<br>
        Deadlock Avoidance and Safe Resource Allocation
    </div>
    """,
    unsafe_allow_html=True
)
