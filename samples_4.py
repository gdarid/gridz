"""
Sample results of lsysto grid
"""
import lsystog as ls

# 4 * 4 patterns
# --------------

if __name__ == '__main__':
    # Central "ABBA" (ABBA for 1221) with "banned" corners
    gp_abba_ban = '/00/_0120_0210_/00/'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=5, patterns=[gp_abba_ban], colors='RBG',
                    banned_colors='/', verbose=True)

    gls.img("sample_images/img_abba_ban.png",  col_fond=(0, 0, 0, 255))

    # Central "ABBA" (ABBA for 1221) with no banned cells
    gp_abba = '0000_0120_0210_0000'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=5, patterns=[gp_abba], colors='RBG',
                    banned_colors='/', verbose=True)

    gls.img("sample_images/img_abba.png",  col_fond=(0, 0, 0, 255))

    # Border (1) with top right corner (2)
    gp_border = '1122_1//1_2//1_1111'

    gls = ls.Lsystg(axiom=None, rules=None, nbiter=5, patterns=[gp_border], colors='RBG',
                    banned_colors='/', verbose=True)

    gls.img("sample_images/img_border.png",  col_fond=(0, 0, 0, 255))
