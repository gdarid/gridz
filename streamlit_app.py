"""
Streamlit application
"""
import streamlit as st
from streamlit.errors import StreamlitAPIException
from loguru import logger

import lsystog as ls


def on_change_selection():
    """
    Change the pattern when the starting pattern is changed

    :return: None
    """
    current_selection = st.session_state.my_selection
    st.session_state.my_pattern = current_selection


@st.cache_data
def load_img(pattern, colors, nb_iterations, apply_rotation):
    """
    Return an image computed from the parameters

    :return: image
    """
    func_transf = ls.strc_2_strc_90 if apply_rotation else None
    try:
        gls = ls.Lsystg(axiom=None, rules=None, nbiter=nb_iterations, patterns=[pattern], colors=colors,
                        banned_colors='/', nb_dest=1, verbose=True, func_transf=func_transf)
        image = gls.img(img_fpath="", col_fond=(0, 0, 0, 255))
    except ls.LsystError as ex:
        st.warning(ex)
        st.stop()
    except Exception as ex:
        st.warning("Please verify your parameters. Special characters are not permitted in the pattern except for '?'")
        logger.error(f"Something went wrong : {ex}")
        st.stop()
    else:
        return image


st.set_page_config(page_title="Gridz", page_icon="🖼️")
st.markdown("# Gridz")

VERBOSE = False  # Set verbose to true for more printed information
first_time = True  # At start, no need to click the draw button

MD1 = """
You have the flexibility to define your own colors and pattern

Simply click on "Draw" when you are satisfied with your new input :sunglasses:
"""

MD2 = """
The possible colors are :
- R : Red
- G : Green
- B : Blue
- W : White
- K : Black
- Y : Yellow
- M : Magenta
- O : Orange
- D : Dim gray
- F : Forest green
- N : Navy
- P : Purple
- T : Background color (black)
- ? : Random color

The pattern assigns colors from left to right and from top to bottom, with each "row" separated by an underscore

The pattern consists of "rotating" colors represented by digits and fixed colors (refer to the available colors mentioned above)

To understand how the pattern functions, try drawing with just one iteration
"""

EXAMPLES_LIST = ['00000_01210_02020_01210_00000', '012_120_201', '1001_0220_0220_1001',
                 '00000_01110_01210_01110_00000', 'T000T_01210_02020_01210_T000T', '00000_01210_02T20_01210_00000',
                 '1112T2_1T12T2_111222_1TTT2T_1TTT2T_1TTT2T']

st.sidebar.markdown(MD1)

input_selection = st.sidebar.selectbox('Choose a starting pattern', EXAMPLES_LIST,
                                       index=0, on_change=on_change_selection, key="my_selection")

EXAMPLES = f"""
Few possible patterns with 3 colors (GRB for example) that you can select

- **:green[{EXAMPLES_LIST[1]}]** ( 3X3 )
- **:green[{EXAMPLES_LIST[2]}]** ( 4X4 )
- **:green[{EXAMPLES_LIST[3]}]** ( 5X5 )
- **:green[{EXAMPLES_LIST[4]}]** ( 5X5 )
- **:green[{EXAMPLES_LIST[5]}]** ( 5X5 )
- **:green[1112T2_1T12T2_..._1TTT2T_1TTT2T]** ( 6X6 )
"""

st.sidebar.markdown(EXAMPLES)

st.sidebar.markdown(MD2)

with st.form("my_form"):
    col = st.text_input('Colors', 'GRB', key='my_colors')
    pat = st.text_input('Pattern', EXAMPLES_LIST[0], key='my_pattern')
    rotation = st.checkbox("90° rotation", True)

    nb_iter = st.number_input('Number of iterations', value=4, min_value=1, max_value=10, format='%d')

    # Every form has a submit button
    submitted = st.form_submit_button("Draw")
    if submitted or first_time:
        first_time = False
        img = load_img(pat, col, nb_iter, rotation)

        try:
            st.write(st.image(img, caption='Generated image'))
        except StreamlitAPIException as exc:
            # Currently : streamlit.errors.StreamlitAPIException: `_repr_html_()` is not a valid Streamlit command.
            if VERBOSE:
                logger.warning(exc)

    st.markdown("---")
    st.markdown(
        "More infos and :star: at [github.com/gdarid/gridz](https://github.com/gdarid/gridz)"
    )
