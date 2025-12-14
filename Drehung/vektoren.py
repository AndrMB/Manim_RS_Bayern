from manim import *
import numpy as np

config.background_color = "#0e0e0e"


def rotate_point(pt, angle, about=(0, 0, 0)):
    pt = np.array(pt, dtype=float)
    if pt.shape[0] == 2:
        pt = np.array([pt[0], pt[1], 0.0])
    about = np.array(about, dtype=float)
    if about.shape[0] == 2:
        about = np.array([about[0], about[1], 0.0])

    v = pt - about
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s],
                  [s, c]])
    v2 = R @ v[:2]
    return np.array([v2[0], v2[1], 0]) + about


class ProgressBar(VGroup):
    def __init__(self, sections, **kwargs):
        super().__init__(**kwargs)
        n = len(sections)
        total_w = 10
        spacing = total_w / (n - 1)
        y = 3.4
        self.circles = VGroup()
        self.lines = VGroup()
        for i in range(n):
            x = -total_w / 2 + i * spacing
            circ = Circle(radius=0.22, stroke_width=2, color=GRAY).move_to([x, y, 0])
            num = Text(str(i + 1), font_size=16).move_to(circ.get_center())
            lbl = Text(sections[i], font_size=14, color=GRAY).next_to(circ, UP, buff=0.08)
            self.add(circ, num, lbl)
            self.circles.add(circ)
            if i > 0:
                x_prev = -total_w / 2 + (i - 1) * spacing
                line = Line([x_prev + 0.22, y, 0], [x - 0.22, y, 0], stroke_width=3, color=GRAY)
                self.add(line)
                self.lines.add(line)

    def set_progress(self, idx):
        for i, circ in enumerate(self.circles):
            if i < idx:
                circ.set_fill(GREEN, 1)
            elif i == idx:
                circ.set_fill(BLUE, 1)
            else:
                circ.set_fill(None, 0)
        for i, line in enumerate(self.lines):
            line.set_color(GREEN if i < idx else GRAY)


class VektorenV6(Scene):
    def construct(self):
        def draw_vector(start, end, color):
            return Arrow(start, end, buff=0, stroke_width=5, color=color)

        # helper for mapping from math coords to NumberPlane points
        def ap(plane, xy):
            x, y = xy
            return plane.coords_to_point(x, y)

        def make_dot_at(plane, xy, color=WHITE):
            return Cross(Dot(ap(plane, xy)), stroke_color=color, stroke_width=3)

        def make_arrow_from_origin(plane, xy, color=BLUE):
            return Arrow(ap(plane, (0, 0)), ap(plane, xy), buff=0, color=color, stroke_width=5)

        def dashed_l(plane, xy, color, isX):
            if (isX):
                start = ap(plane, (0, 0))
                end = ap(plane, (xy[0], 0))
                value = str(xy[0])
            else:
                start = ap(plane, (xy[0], 0))
                end = ap(plane, (xy[0], xy[1]))
                value = str(xy[1])

            line = DashedLine(start, end, color=color, dash_length=0.12, stroke_opacity=0.7)
            num = MathTex(value, color=color).scale(0.7).move_to((start + end) / 2)
            return line, num

        # progressbar and plain
        prog = ProgressBar(["180°", "90°", "-90°", "P' berechnen"])
        self.play(FadeIn(prog))
        prog.set_progress(0)

        plane = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-3, 4, 1],
            background_line_style={"stroke_color": GREY, "stroke_width": 1, "stroke_opacity": 0.35},
            axis_config={"stroke_color": GREY_B, "stroke_width": 2, "stroke_opacity": 0.8, "include_tip": True},
        ).add_coordinates(font_size=20, stroke_width=1, num_decimal_places=0).scale(0.95)
        self.play(Create(plane))

        # ---------------- PART 1: 180° ----------------
        # Points
        Z = make_dot_at(plane, (0, 0), color=YELLOW)
        P_coords = (3, 2)
        P = make_dot_at(plane, P_coords, color=BLUE)
        Z_label = MathTex("Z (0|0)").next_to(Z, UL, buff=0.06)
        P_label = MathTex("P (3|2)").next_to(P, UR, buff=0.06)
        self.play(FadeIn(Z, P, P_label, Z_label))
        self.wait(0.5)

        # Vector
        vZP = draw_vector(Z, P, color=BLUE)
        zpv_label = MathTex(r"\vec{ZP} = \begin{pmatrix}3\\2\end{pmatrix}").next_to(vZP, UR, buff=0.06)
        self.play(FadeOut(Z_label, P_label, P), Create(vZP), Write(zpv_label), run_time=0.5)
        self.wait(0.5)

        # rotation
        vZP_copy = vZP.copy()
        self.play(Rotate(vZP_copy, PI, about_point=ap(plane, (0, 0))))
        self.wait(0.5)
        zpvP_label = MathTex(r"\vec{ZP'} = \begin{pmatrix}-3\\-2\end{pmatrix}").next_to(vZP_copy.get_tip(), LEFT,
                                                                                        buff=0.06)

        self.play(Write(zpvP_label), FadeToColor(vZP_copy, GREEN))
        self.wait(0.5)

        # Koordinatendreiecke
        x_line_orig, x_text_orig = dashed_l(plane, (3, 2), YELLOW, True)
        y_line_orig, y_text_orig = dashed_l(plane, (3, 2), RED, False)
        x_line_img, x_text_img = dashed_l(plane, (-3, -2), YELLOW, True)
        y_line_img, y_text_img = dashed_l(plane, (-3, -2), RED, False)

        self.play(Create(x_line_orig), Create(y_line_orig), Write(x_text_orig), Write(y_text_orig))
        self.play(Create(x_line_img), Create(y_line_img), Write(x_text_img), Write(y_text_img))
        self.wait(0.5)
        # ---------- Repeat mit Koo-Dreieck ----------
        rotGroup = VGroup(x_line_orig, y_line_orig, vZP)
        rotGroup_copy = rotGroup.copy()
        self.play(Rotate(rotGroup_copy, PI, about_point=Z.get_center()), run_time=2)

        rule_180 = MathTex(r"\begin{pmatrix}x\\y\end{pmatrix} \mapsto \begin{pmatrix}-x\\-y\end{pmatrix}",
                           color=ORANGE).scale(
            1).move_to(DOWN * 3 + RIGHT * 3)
        self.play(Write(rule_180))
        self.wait(0.5)

        # cleanup
        self.play(
            FadeOut(x_line_orig, y_line_orig, x_text_orig, y_text_orig, x_line_img, y_line_img, x_text_img, y_text_img,
                    zpv_label, vZP, vZP_copy, zpvP_label, Z, rotGroup_copy, rule_180), run_time=0.5)
        self.wait(0.5)

        # ---------------- PART 2: +90° ----------------
        prog.set_progress(1)
        P_coords = (3, 2)
        vZP = make_arrow_from_origin(plane, P_coords, color=BLUE)
        vZP_label = MathTex(r"\vec{ZP} = \begin{pmatrix}3\\2\end{pmatrix}").next_to(vZP, UR, buff=0.06)
        # coordinate triangle displayed first
        x_line, x_num = dashed_l(plane, P_coords, YELLOW, True)
        y_line, y_num = dashed_l(plane, P_coords, RED, False)
        self.play(Create(vZP), Create(x_line), Create(y_line), FadeIn(Z), Write(x_num), Write(y_num), Write(vZP_label))
        self.wait(0.5)

        # copy everything and rotate the copies
        x_num_c, y_num_c = x_num.copy(), y_num.copy()
        vZP_copy = vZP.copy()
        group_copy = VGroup(vZP_copy, x_line.copy(), y_line.copy(), x_num_c, y_num_c)
        self.play(Rotate(group_copy, PI / 2, about_point=ap(plane, (0, 0))))
        self.wait(0.5)
        new_y_num_c = MathTex(r"-2", color=RED).scale(0.7).move_to(y_num_c.get_center())
        self.play(Rotate(x_num_c, -PI / 2, about_point=x_num_c.get_center()), Transform(y_num_c, new_y_num_c))
        self.wait(0.5)

        # create independent image arrow and dot (green) at rotated coords
        vec_label = MathTex(r"\vec{ZP'} = \begin{pmatrix}-2\\3\end{pmatrix}").next_to(vZP_copy.get_center() + LEFT / 3,
                                                                                      LEFT,
                                                                                      buff=0.06)
        self.play(FadeToColor(vZP_copy, GREEN), Write(vec_label))
        self.wait(0.5)
        rule_90 = MathTex(r"\begin{pmatrix}x\\y\end{pmatrix} \mapsto \begin{pmatrix}-y\\x\end{pmatrix}",
                          color=ORANGE).scale(
            1).move_to(DOWN * 3 + LEFT * 3)
        self.play(Write(rule_90))
        self.wait(0.5)

        self.wait(0.5)
        # cleanup: keep originals, remove image overlay objects
        self.play(FadeOut(Z, vec_label, group_copy, rule_90, vZP, x_line, y_line, x_num, y_num, vZP_label),
                  run_time=0.5)
        self.wait(0.5)

        # ---------------- PART 3: -90° (same procedure) ----------------
        prog.set_progress(2)
        P_coords = (3, 2)
        vZP = make_arrow_from_origin(plane, P_coords, color=BLUE)
        vZP_label = MathTex(r"\vec{ZP} = \begin{pmatrix}3\\2\end{pmatrix}").next_to(vZP, UR, buff=0.06)
        # coordinate triangle displayed first
        x_line, x_num = dashed_l(plane, P_coords, YELLOW, True)
        y_line, y_num = dashed_l(plane, P_coords, RED, False)
        self.play(Create(vZP), Create(x_line), Create(y_line), FadeIn(Z), Write(x_num), Write(y_num), Write(vZP_label))
        self.wait(0.5)

        # copy everything and rotate the copies
        x_num_c, y_num_c = x_num.copy(), y_num.copy()
        vZP_copy = vZP.copy()
        group_copy = VGroup(vZP_copy, x_line.copy(), y_line.copy(), x_num_c, y_num_c)
        self.play(Rotate(group_copy, -PI / 2, about_point=ap(plane, (0, 0))))
        self.wait(0.5)
        new_x_num_c = MathTex(r"-3", color=YELLOW).scale(0.7).move_to(x_num_c.get_center())
        self.play(Rotate(y_num_c, +PI / 2, about_point=y_num_c.get_center()), Transform(x_num_c, new_x_num_c))
        self.wait(0.5)

        vec_label = MathTex(r"\vec{ZP'} = \begin{pmatrix}2\\-3\end{pmatrix}").next_to(vZP_copy.get_center(), RIGHT,
                                                                                      buff=0.06)
        self.play(Write(vec_label), FadeToColor(vZP_copy, GREEN))
        self.wait(0.5)
        rule_90 = MathTex(r"\begin{pmatrix}x\\y\end{pmatrix} \mapsto \begin{pmatrix}y\\-x\end{pmatrix}",
                          color=ORANGE).scale(
            1).move_to(DOWN * 3 + LEFT * 3)
        self.play(Write(rule_90))
        self.wait(0.5)

        self.wait(0.5)
        # cleanup: keep originals, remove image overlay objects
        self.play(FadeOut(Z, vec_label, group_copy, rule_90, vZP, x_line, y_line, x_num, y_num, vZP_label),
                  run_time=0.5)
        self.wait(0.5)

        # ---------------- PART 4: P' Berechnung (use your original layout style) ----------------
        # Z = make_dot_at(plane, (0, 0), color=YELLOW)
        # P_coords = (3, 2)
        # P = make_dot_at(plane, P_coords, color=BLUE)
        # Z_label = MathTex("Z").next_to(Z, UR, buff=0.06)

        prog.set_progress(3)
        Z = make_dot_at(plane, (-2, 0), color=YELLOW)
        Z_label = MathTex("Z (-2|0)").next_to(Z, DOWN, buff=0.05)
        P = make_dot_at(plane, (1, 2), color=BLUE)
        P_label = MathTex("P (1|2)").next_to(P, UR, buff=0.05)
        self.play(FadeIn(Z, P), Write(Z_label), Write(P_label))
        self.wait(0.5)

        vZP = draw_vector(Z.get_center(), P.get_center(), BLUE)
        vZP_label = MathTex(r"\vec{ZP} = \begin{pmatrix}3\\2\end{pmatrix}").next_to(vZP, UR, buff=0.06)
        self.play(FadeOut(Z_label, P_label), Create(vZP), Write(vZP_label), run_time=0.5)
        self.wait(0.5)

        vZP_copy = vZP.copy()
        P_copy = P.copy()
        rotGroup = VGroup(vZP_copy, P_copy)
        self.play(Rotate(rotGroup, PI / 2, about_point=Z.get_center()))
        self.play(FadeToColor(vZP_copy, GREEN),
                  FadeToColor(P_copy, GREEN))
        self.wait(0.5)
        vZPp_label = MathTex(r"\vec{ZP'} = \begin{pmatrix}-2\\3\end{pmatrix}").next_to(vZP_copy.get_center() + LEFT / 3,
                                                                                       LEFT,
                                                                                       buff=0.06)

        self.play(TransformFromCopy(vZP_label, vZPp_label))
        self.wait(0.5)

        P_copy_label = MathTex("P'=?").next_to(P_copy, UL, buff=0.05)
        self.play(Write(P_copy_label))
        self.wait(0.5)
        vOPp = draw_vector(ap(plane, (0, 0)), P_copy.get_center(), RED)
        vOPp_label = MathTex(r"\vec{OP'}", color=RED).next_to(vOPp.get_center(), UR, buff=0.05)
        vOZ = draw_vector(ap(plane, (0, 0)), Z.get_center(), YELLOW)
        self.play(FadeIn(vOPp), Write(vOPp_label), FadeIn(vOZ))
        self.wait(0.5)
        self.play(Indicate(vOPp, scale_factor=1.2, color=RED), run_time=0.5)
        self.wait(0.5)
        self.play(Indicate(vOZ, scale_factor=1.2, color=YELLOW), Indicate(vZP_copy, scale_factor=1.5, color=GREEN),
                  run_time=0.5)
        self.wait(0.5)

        # irrelevante teile auslbenden
        irrelevantGrp = VGroup(vOPp, vOPp_label, vZP, vZP_label, P)
        self.play(irrelevantGrp.animate.fade(0.7))

        # Now the formula. We'll substitute visually.
        # Einzelteile der Formel
        L1_left = MathTex(r"\vec{OP'} = ")
        oz_symbol = MathTex(r"\vec{OZ}")
        plus = MathTex(r"+")
        zp_symbol = MathTex(r"\vec{ZP'}")

        # Positionieren: alle nebeneinander setzen
        L1_group = VGroup(L1_left, oz_symbol, plus, zp_symbol).arrange(RIGHT, buff=0.15).to_edge(DOWN)
        self.play(Write(L1_group))
        self.wait(0.5)

        # show vOZ
        vOZ_label = MathTex(r"\vec{OZ} = \begin{pmatrix}-2\\0\end{pmatrix}", color=YELLOW).next_to(vOZ.get_center(),
                                                                                                   DOWN, buff=0.05)
        self.play(Write(vOZ_label))
        self.wait(0.5)

        oz_value = MathTex(r"\begin{pmatrix}-2\\0\end{pmatrix}").scale(0.75).move_to(oz_symbol.get_center())
        zp_value = MathTex(r"\begin{pmatrix}-2\\3\end{pmatrix}").scale(0.75).move_to(zp_symbol.get_center())

        # Animation: die Werte „fliegen“ in die Formel
        self.play(
            Transform(oz_symbol, oz_value),
            Transform(zp_symbol, zp_value)
        )
        self.wait(0.5)

        # compute final result
        result = MathTex(r"=", r"\begin{pmatrix}-4\\3\end{pmatrix}").next_to(zp_symbol, RIGHT, buff=0.2)
        self.play(Write(result))
        self.wait(0.5)

        # label P' on plane
        label_pp = MathTex(r"P' (-4|3)").next_to(P_copy, UL, buff=0.05)
        self.play(Transform(P_copy_label, label_pp))
        self.wait(2)
