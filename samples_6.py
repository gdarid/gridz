"""
Sample results of lsysto grid
"""
import lsystog as ls

# 6 * 6 patterns
# --------------

if __name__ == '__main__':
    # PY (P is in 1, Y is in 2) with a banned background and a 90° rotation applied for each iteration
    gp_py = '1112/2_1/12/2_111222_1///2/_1///2/_1///2/'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=4, patterns=[gp_py], colors='RBG', banned_colors='/', verbose=True,
                    func_transf=ls.strc_2_strc_90)

    gls.img("sample_images/img_py.png",  col_fond=(0, 0, 0, 255))
