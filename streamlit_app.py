import streamlit as st
import lsystog as ls
from streamlit.errors import StreamlitAPIException


def on_change_selection():
    current_selection = st.session_state.my_selection
    # pattern = examples_list[current_selection]
    st.session_state.my_pattern = current_selection


@st.cache_data
def load_img(pattern, colors, nb_iterations):
    try:
        gls = ls.Lsystg(axiom=None, rules=None, nbiter=nb_iterations, patterns=[pattern], colors=colors,
                        banned_colors='/', nb_dest=1, verbose=True)
        image = gls.img(img_fpath="", col_fond=(0, 0, 0, 255))
    except ls.LsystError as ex:
        st.warning(ex)
        st.stop()
    except Exception as ex:
        st.warning("Please verify your parameters. Special characters are not permitted in the pattern except for '?'")
        print(f"Something went wrong : {ex}")
        st.stop()
    else:
        return image


st.set_page_config(page_title="Gridz", page_icon="🖼️")
st.markdown("# Gridz")

verbose = False  # Set verbose to true for more printed information
first_time = True  # At start, no need to click the draw button

md1 = """
You have the flexibility to define your own colors and pattern

Simply click on "Draw" when you are satisfied with your new input :sunglasses:
"""

md2 = """
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

examples_list = ['00000_01210_02020_01210_00000', '012_120_201', '1001_0220_0220_1001',
                 '00000_01110_01210_01110_00000', 'T000T_01210_02020_01210_T000T', '00000_01210_02T20_01210_00000']

st.sidebar.markdown(md1)

input_selection = st.sidebar.selectbox('Choose a starting pattern', examples_list,
                                       index=0, on_change=on_change_selection, key="my_selection")

examples = f"""
Few possible patterns with 3 colors (GRB for example) that you can select

- **:green[{examples_list[1]}]** ( 3X3 )
- **:green[{examples_list[2]}]** ( 4X4 )
- **:green[{examples_list[3]}]** ( 5X5 )
- **:green[{examples_list[4]}]** ( 5X5 )
- **:green[{examples_list[5]}]** ( 5X5 )
"""

st.sidebar.markdown(examples)

st.sidebar.markdown(md2)

with st.form("my_form"):
    # 0000_0120_0210_0000 ... 00000_01/10_02020_01210_00000
    col = st.text_input('Colors', 'GRB', key='my_colors')
    pat = st.text_input('Pattern', examples_list[0], key='my_pattern')

    nb_iter = st.number_input('Number of iterations', value=4, min_value=1, max_value=10, format='%d')

    # Every form has a submit button
    submitted = st.form_submit_button("Draw")
    if submitted or first_time:
        first_time = False
        img = load_img(pat, col, nb_iter)

        try:
            st.write(st.image(img, caption='Generated image'))
        except StreamlitAPIException as exc:
            # Currently : streamlit.errors.StreamlitAPIException: `_repr_html_()` is not a valid Streamlit command.
            if verbose:
                print(exc)

    st.markdown("---")
    st.markdown(
        "More infos and :star: at [github.com/gdarid/gridz](https://github.com/gdarid/gridz)"
    )
