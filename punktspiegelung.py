from manim import *
import numpy as np

config.background_color = "#0e0e0e"


def rotate_point(pt, angle, about=np.array([0, 0, 0])):
    v = np.array(pt) - np.array(about)
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    v2 = R @ v[:2]
    return np.array([v2[0], v2[1], 0]) + np.array(about)


class ProgressBar(VGroup):
    def __init__(self, sections, **kwargs):
        super().__init__(**kwargs)
        n = len(sections)
        total_w = 10
        spacing = total_w / (n - 1)
        y = 3.4
        self.circles = VGroup()
        self.lines = VGroup()
        self.labels = VGroup()
        for i in range(n):
            x = -total_w / 2 + i * spacing
            circ = Circle(radius=0.22, stroke_width=2, color=GRAY).move_to([x, y, 0])
            num = Text(str(i + 1), font_size=16).move_to(circ.get_center())
            lbl = Text(sections[i], font_size=14, color=GRAY).next_to(circ, UP, buff=0.08)
            self.add(circ, num, lbl)
            self.circles.add(circ)
            self.labels.add(lbl)
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
            line.set_color(GREEN if i < idx - 0 else GRAY)


class PunktspiegelungV4(Scene):
    def construct(self):
        config.tex_template.add_to_preamble(r"\usepackage{mathtools}")
        sections = ["Definition", "Eigenschaften", "Drehung", "Bestimmung von Z"]
        prog = ProgressBar(sections)
        self.play(FadeIn(prog))
        prog.set_progress(0)
        self.add(prog)

        # ---------- 1) Definition ----------
        prog.set_progress(0)

        # Place Z at origin (outside triangle)
        Z = Dot(ORIGIN, color=YELLOW)
        Z_label = MathTex("Z").next_to(Z, DOWN, buff=0.08)

        # Triangle placed so Z is not inside (to the right of Z)
        tri_ur = Polygon([1, -2, 0], [3, -2, 0], [2, 0.5, 0], color=BLUE, fill_opacity=0.8, stroke_width=3)
        # tri_img = rotation of tri_ur around Z
        tri_img = tri_ur.copy().rotate(PI, about_point=Z.get_center()).set_color(GREEN).set_opacity(0.8)

        # vertices and dots + labels (labels BEFORE rotation)
        verts_ur = tri_ur.get_vertices()
        verts_img = tri_img.get_vertices()
        dots_ur = [Cross(Dot(v), stroke_width=3, stroke_color=BLUE) for v in verts_ur]
        labels_ur = [MathTex("P"), MathTex("Q"), MathTex("R")]
        for lab, d in zip(labels_ur, dots_ur):
            lab.next_to(d, UR, buff=0.05)

        # show original triangle and labels and Z
        self.play(Create(tri_ur), FadeIn(Z), Write(Z_label))
        self.play(*[FadeIn(d) for d in dots_ur], *[Write(l) for l in labels_ur])
        self.wait(0.5)
        tri_move = tri_ur.copy()

        notation = MathTex(r"PQR \xmapsto{Z;\ \varphi = 180^\circ} P'Q'R'").scale(1.0).move_to(
            DOWN * 3)
        self.play(Write(notation))

        # now create image by rotation (so P'Q'R' is exactly rotated copy)
        self.play(Rotate(tri_move, PI, about_point=Z.get_center()))
        self.wait(0.5)
        # but actually display tri_img (rotated copy) and its dots/labels
        dots_img = [Cross(Dot(v), stroke_width=3, stroke_color=GREEN) for v in verts_img]
        labels_img = [MathTex("P'"), MathTex("Q'"), MathTex("R'")]
        for lab, d in zip(labels_img, dots_img):
            lab.next_to(d, UR, buff=0.05)
        self.play(FadeIn(tri_img), *[FadeIn(d) for d in dots_img], *[Write(l) for l in labels_img])
        self.wait(0.5)
        self.play(FadeOut(notation))

        # connection lines PP', QQ', RR'
        for i in range(3):
            seg = Line(verts_ur[i], verts_img[i], color=ORANGE)
            self.play(Create(seg))
            self.wait(0.15)
            self.play(FadeOut(seg), run_time=0.5)

        # keep tri_ur and tri_img visible for a moment
        self.wait(0.4)
        final_text = Text("Punktspiegelung = Drehung um 180°", color=ORANGE, font_size=28).move_to(DOWN * 3)
        self.play(Write(final_text))
        self.wait(0.5)

        self.play(FadeOut(tri_ur, tri_img, *dots_ur, *dots_img, *labels_ur, *labels_img, Z, Z_label, tri_move,
                          final_text), run_time=0.5)
        self.wait(0.5)

        # ---------- 2) Eigenschaften ----------
        prog.set_progress(1)
        Z2 = Dot(ORIGIN, color=YELLOW)
        Z2_label = MathTex("Z").next_to(Z2, DOWN, buff=0.08)

        # Full line (infinite-looking) through screen: blue, with two points at different distances
        full_line = Line(LEFT * 6, RIGHT * 6, color=BLUE)
        line_label = MathTex("g").next_to(full_line, DOWN, buff=0.08).move_to(LEFT * 2 + DOWN/3)

        notation = MathTex(r"g \xmapsto{Z;\ \varphi = 180^\circ} g'").scale(1.0).move_to(DOWN * 3)
        self.play(FadeIn(full_line), FadeIn(Z2), FadeIn(Z2_label))
        self.play(Write(line_label), Write(notation))
        self.wait(0.5)

        Line_rot = full_line.copy()
        # rotate the whole line+points (group) by 180° around Z2 -> becomes green image
        self.play(Rotate(Line_rot, PI, about_point=Z2.get_center()))

        linep_label = MathTex("g'").next_to(full_line, DOWN, buff=0.08).move_to(RIGHT * 2 + DOWN/3)
        self.wait(0.5)
        self.play(FadeToColor(Line_rot, GREEN), FadeIn(linep_label), FadeOut(notation))
        self.wait(0.5)
        final_text = Text("Jede Gerade durch Z ist Fixgerade", color=ORANGE, font_size=28).move_to(DOWN * 3)
        self.play(Write(final_text))
        self.wait(0.5)
        self.play(
            FadeOut(full_line, Line_rot, Z2, Z2_label, final_text, linep_label, line_label),
            run_time=0.5)
        self.wait(0.5)

        # ---------- 3) Konstruktion ----------
        prog.set_progress(2)
        plane = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-3, 4, 1],
            background_line_style={"stroke_color": GREY, "stroke_width": 1, "stroke_opacity": 0.35},
            axis_config={"stroke_color": GREY_B, "stroke_width": 2, "stroke_opacity": 0.8, "include_tip": True},
        ).add_coordinates(font_size=20, stroke_width=1, num_decimal_places=0).scale(0.95)
        self.play(Create(plane))

        Z4 = Cross(Dot(plane.coords_to_point(0, 0)), stroke_width=2, stroke_color=YELLOW)
        Z4_label = MathTex("Z").next_to(Z4, DOWN, buff=0.08)
        P = Cross(Dot(plane.coords_to_point(-2, 1)), stroke_width=2, stroke_color=BLUE)
        Q = Cross(Dot(plane.coords_to_point(-1, -1)), stroke_width=2, stroke_color=BLUE)
        P_label = MathTex("P (-2|1)").next_to(P, UL, buff=0.05)
        Q_label = MathTex("Q (-1|-1)").next_to(Q, DL, buff=0.05)
        notation = MathTex(r"\overline{PQ} \xmapsto{Z;\ \varphi = 180^\circ} \overline{P'Q'}").scale(1.0).move_to(
            DOWN * 3)

        self.play(FadeIn(Z4), Write(Z4_label), FadeIn(P), FadeIn(Q), Write(P_label), Write(Q_label), Write(notation))

        # finite segment PQ (only between points)
        PQ_seg = Line(P.get_center(), Q.get_center(), color=BLUE)
        self.play(Create(PQ_seg))
        self.wait(0.5)

        # draw PZ and extend past Z by same length to get P'
        PZ = Line(P.get_center(), Z4.get_center(), color=ORANGE)
        QZ = Line(Q.get_center(), Z4.get_center(), color=ORANGE)
        self.play(Create(PZ), Create(QZ))
        self.wait(0.5)
        Pp = Cross(Dot(plane.coords_to_point(2, -1)), stroke_width=2, stroke_color=GREEN)
        Qp = Cross(Dot(plane.coords_to_point(1, 1)), stroke_width=2, stroke_color=GREEN)
        Pp_label = MathTex("P' (2|-1)").next_to(Pp, UR, buff=0.05)
        Qp_label = MathTex("Q' (1|1)").next_to(Qp, RIGHT, buff=0.05)
        # show extended lines from Z to P' and Z to Q'
        extP = Line(Z4.get_center(), Pp.get_center(), color=ORANGE)
        extQ = Line(Z4.get_center(), Qp.get_center(), color=ORANGE)
        self.play(Create(extP), Create(extQ))
        self.play(FadeIn(Pp), FadeIn(Qp), Write(Pp_label), Write(Qp_label))
        self.wait(0.5)

        # draw green segment P'Q' to show target
        PpQp_seg = Line(Pp.get_center(), Qp.get_center(), color=GREEN)
        self.play(Create(PpQp_seg))
        # remove the construction helper lines (PZ, QZ, ext lines) BEFORE the rotation demo
        self.play(FadeOut(PZ, QZ, extP, extQ), run_time=0.5)
        self.wait(0.5)

        rot = PQ_seg.copy()
        # Now rotate original PQ_seg and points by 180° to show they match P'Q'
        self.play(Rotate(rot, PI, about_point=Z4.get_center()))
        self.play(FadeToColor(rot, (GREEN + BLUE)))
        self.wait(0.5)
        # leave P', Q' visible, fade rotated originals (they coincide)
        self.play(
            FadeOut(rot, P, Q, PQ_seg, Pp, Qp, Pp_label, Qp_label, PpQp_seg, Z4, Z4_label, P_label, Q_label, notation),
            run_time=0.5)
        self.wait(0.5)

        # ---------- 4) Bestimmung ----------
        prog.set_progress(3)
        # create triangle and derive image by 180° rotation (Punktspiegelung)
        tri_ur = Polygon(plane.coords_to_point(-2.5, -1), plane.coords_to_point(-1, -2),
                         plane.coords_to_point(-2, 1), color=BLUE, fill_opacity=0.8, stroke_width=3)
        verts_ur = tri_ur.get_vertices()
        # echte Punktspiegelung: alle Koordinaten negieren
        verts_img = [-v for v in verts_ur]
        tri_img = Polygon(*verts_img, color=GREEN, fill_opacity=0.8, stroke_width=3)

        verts_ur = tri_ur.get_vertices()
        verts_img = tri_img.get_vertices()
        dots_ur = [Cross(Dot(v), stroke_width=2, stroke_color=BLUE) for v in verts_ur]
        dots_img = [Cross(Dot(v), stroke_width=2, stroke_color=GREEN) for v in verts_img]
        labels_ur = [MathTex("P"), MathTex("Q"), MathTex("R")]
        labels_img = [MathTex("P'"), MathTex("Q'"), MathTex("R'")]
        for lab, v in zip(labels_ur, verts_ur): lab.next_to(v, UR, buff=0.05)
        for lab, v in zip(labels_img, verts_img): lab.next_to(v, UR, buff=0.05)

        self.play(Create(tri_ur), *[FadeIn(d) for d in dots_ur], *[Write(l) for l in labels_ur])
        self.play(Create(tri_img), *[FadeIn(d) for d in dots_img], *[Write(l) for l in labels_img])
        self.wait(0.5)

        # Draw PP' for first vertex and compute midpoint -> Z
        P_ur = verts_ur[0]
        P_img = verts_img[0]
        seg_PPp = Line(P_ur, P_img, color=ORANGE)
        self.play(Create(seg_PPp))
        mid = (P_ur + P_img) / 2
        Z_mid = Cross(Dot(mid), stroke_color=YELLOW, stroke_width=3)
        Z_label = MathTex("Z").next_to(Z_mid, DOWN, buff=0.05)
        self.play(FadeIn(Z_mid), Write(Z_label))
        self.wait(0.5)

        # alternativ anderen beiden linien
        Q_ur = verts_ur[1]
        Q_img = verts_img[1]
        seq_QQp = Line(Q_ur, Q_img, color=ORANGE)
        R_ur = verts_ur[2]
        R_img = verts_img[2]
        seq_RRp = Line(R_ur, R_img, color=ORANGE)
        self.play(Create(seq_QQp), Create(seq_RRp))
        self.wait(0.5)
        self.play(FadeOut(seq_QQp, seq_RRp), run_time=0.5)
        self.wait(0.5)

        # Remove labels from (3) if any remain (conservative)
        # Now rotate tri_ur about Z_mid and show that it matches tri_img
        rot = tri_ur.copy()
        self.play(Rotate(rot, PI, about_point=Z_mid.get_center()))
        # visual confirmation: tint same color
        self.play(FadeToColor(rot, (GREEN + BLUE)))
        self.wait(2)
