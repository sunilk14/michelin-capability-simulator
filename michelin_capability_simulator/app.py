"""Michelin capability allocation exercise — Streamlit classroom application."""
import hmac
import streamlit as st
from model import CAPABILITIES, BUDGET, MINIMUM, validate_allocation, calculate_outcomes
from storage import get_submissions, save_submission, use_google_sheets, secret

st.set_page_config(page_title='Michelin Capability Challenge', page_icon='🚚', layout='wide')
st.title('🚚 Michelin Connected-Tyre Capability Challenge')
st.caption('Teaching simulation: all budgets, thresholds and scoring rules are illustrative—not Michelin company data.')

student_tab, faculty_tab = st.tabs(['Student simulation', 'Faculty dashboard'])

with student_tab:
    st.markdown('### The challenge')
    st.info('Michelin can put sensors in tyres. But can it turn connected-tyre data into reliable maintenance services and new business models? You have **100 points** to invest in eight complementary capabilities. Allocate all 100 to submit.')
    if not use_google_sheets():
        st.warning('Local demo mode: submissions are stored in a CSV on this server. On Streamlit Community Cloud, they may disappear after a restart. Configure Google Sheets before sharing with students.')

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        section = st.selectbox('Class section', ['A', 'B'], key='section')
    with c2:
        group = st.text_input('Group ID (e.g., 01)', max_chars=20, key='group_id')
    with c3:
        round_name = st.selectbox('Round', ['1'], help='Round 1 is included in this starter version.')

    st.markdown('### Allocate your capability points')
    st.caption('Each slider moves in steps of 5, from 0 to 50 points. A capability becomes basically ready at 15 points, but your budget cannot fully fund all eight.')
    allocation = {}
    for i, (name, description) in enumerate(CAPABILITIES.items()):
        left, right = st.columns([3, 2], vertical_alignment='center')
        with left:
            allocation[name] = st.slider(name, min_value=0, max_value=50, value=0,
                                         step=5, key=f'cap_{i}')
        with right:
            st.caption(description)

    total = sum(allocation.values())
    remaining = BUDGET - total
    st.progress(min(total/BUDGET, 1.0), text=f'{total} / {BUDGET} points allocated')
    if total > BUDGET:
        st.error(f'Over budget by {total - BUDGET} points. Reduce your allocation.')
    elif total < BUDGET:
        st.warning(f'{remaining} points remain. Allocate exactly 100 before submitting.')
    else:
        st.success('Budget fully allocated — ready to submit.')

    scores = calculate_outcomes(allocation)
    with st.expander('Preview: how the simulation evaluates your capability mix'):
        st.write('Capability readiness is assessed at 15 points. Outcomes are constrained by their weakest necessary component.')
        m1,m2,m3,m4 = st.columns(4)
        m1.metric('Capabilities ≥15', f"{scores['Ready capabilities']}/8")
        m2.metric('Predictive insight', scores['Predictive insight'])
        m3.metric('Actionable service', scores['Actionable service'])
        m4.metric('Commercial readiness', scores['Commercial readiness'])
        st.caption('Scores are classroom heuristics, not predictions or monetary returns.')

    valid, message = validate_allocation(allocation)
    submitted = st.button('Submit group allocation', type='primary', disabled=not(valid and group.strip()), use_container_width=True)
    if submitted:
        cleaned_group = group.strip()
        try:
            ok, feedback = save_submission(section, cleaned_group, round_name, allocation)
            if ok:
                st.success(f'{feedback} Section {section} / Group {cleaned_group}.')
                st.balloons()
            else:
                st.error(feedback)
        except Exception:
            st.error('Unable to save your submission. Contact the instructor; do not assume it was recorded.')
    st.markdown('---')
    st.markdown('**Reflection:** If every competitor can buy the same sensors and AI tools, why are connected-tyre services still difficult to imitate?')

with faculty_tab:
    st.markdown('### Faculty dashboard')
    st.caption('This page is password protected with a shared faculty password. For higher-security deployments, use individual authentication and an access-controlled backend.')
    expected = secret('faculty_password', '')
    if not expected:
        st.error('Faculty dashboard is disabled until faculty_password is configured in Streamlit secrets.')
    else:
        entered = st.text_input('Faculty password', type='password')
        if entered and hmac.compare_digest(entered, expected):
            if st.button('Refresh submissions'):
                st.rerun()
            try:
                df = get_submissions()
            except Exception:
                st.error('Could not read submissions. Verify the spreadsheet and credentials.')
            else:
                st.metric('Total submissions', len(df))
                if df.empty:
                    st.info('No group submissions recorded yet.')
                else:
                    f1, f2 = st.columns(2)
                    with f1:
                        selected_section = st.selectbox('Filter section', ['All', 'A', 'B'])
                    with f2:
                        metric = st.selectbox('Compare on', ['Commercial readiness', 'Actionable service', 'Predictive insight', 'Ready capabilities'])
                    filtered = df if selected_section == 'All' else df[df['section'].astype(str)==selected_section]
                    st.bar_chart(filtered.set_index(filtered['section'].astype(str)+' / '+filtered['group'].astype(str))[metric].apply(lambda x: float(x)))
                    st.dataframe(filtered, hide_index=True, use_container_width=True)
                    st.download_button('Download CSV', filtered.to_csv(index=False).encode('utf-8'), 'michelin_submissions.csv', 'text/csv')
        elif entered:
            st.error('Incorrect password.')
