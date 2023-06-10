"""
Sample results of lsysto grid
"""
import lsystog as ls

# 3 * 3 patterns
# --------------

if __name__ == '__main__':
    # L shape (100_100_111) and top right corner (002_000_000) with "banned" background ( "0" )
    gp_rst_ban = '1/2_1//_111'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=6, patterns=[gp_rst_ban], colors='RBG',
                    banned_colors='/', verbose=True)

    gls.img("sample_images/img_rst_ban.png",  col_fond=(0, 0, 0, 255))

    # L shape and top right corner (the background is not banned)
    gp_rst = '102_100_111'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=6, patterns=[gp_rst], colors='RBG',
                    banned_colors='/', verbose=True)

    gls.img("sample_images/img_rst.png",  col_fond=(0, 0, 0, 255))

    # It is possible to use the random color (?) - L shape and top right corner (the background "0" is not banned)
    gp_rst = '102_100_111'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=6, patterns=[gp_rst], colors='RBG?',
                    banned_colors='/', verbose=True)

    gls.img("sample_images/img_rst_rnd.png",  col_fond=(0, 0, 0, 255))
