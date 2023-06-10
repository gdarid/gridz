import streamlit as st
import lsystog as ls
from streamlit.errors import StreamlitAPIException


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
        st.warning("Something went wrong, please check your parameters")
        print(f"Something went wrong : {ex}")
        st.stop()
    else:
        return image


st.set_page_config(page_title="Gridz", page_icon="🖼️")
st.markdown("# Gridz")

verbose = False  # Set verbose to true for more printed information
first_time = True  # At start, no need to click the draw button

md = """
You can specify your own colors and your own pattern 

Just click "Draw", when your new input is OK :sunglasses:

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

The pattern gives the colors from left to right
and from up to down (the "rows" are separated with an underscore)

The pattern is made of "rotating" colors represented by digits and fixed colors (see the possible colors above)

Draw with one iteration to see how the pattern works
"""

st.sidebar.markdown(md)

with st.form("my_form"):
    # 0000_0120_0210_0000 ... 00000_01/10_02020_01210_00000
    col = st.text_input('Colors', 'GRB')
    pat = st.text_input('Pattern', '00000_01210_02020_01210_00000')

    examples = """
    Few possible patterns with 3 colors that you may copy and paste above
    
    - 012_120_201 ( 3X3 )
    - 1001_0220_0220_1001 ( 4X4 )
    - 00000_01110_01210_01110_00000 ( 5X5 )
    - T0000_01210_02020_01210_0000T ( 5X5 )
    - 00000_01210_02T20_01210_00000 ( 5X5 )
    """

    st.markdown(examples)

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
