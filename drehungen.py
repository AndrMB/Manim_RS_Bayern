from manim import *
import numpy as np

# ---------- Config ----------
config.background_color = "#0e0e0e"


# config.pixel_width = 1920
# config.pixel_height = 1080
# config.frame_height = 8.0
# config.frame_width = 8.0 * 16 / 9


# ---------- Helpers ----------
def rotate_point(pt, angle, about=np.array([0, 0, 0])):
    v = np.array(pt) - np.array(about)
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    v2 = R @ v[:2]
    return np.array([v2[0], v2[1], 0]) + np.array(about)


def make_windmill_three(radius=1.6, color=BLUE):
    """
    Windrad mit 3 klaren Dreiecken (spitz nach außen) und einer Nabe (Dot).
    Rückgabe: blades (VGroup), center (Dot)
    """
    blades = VGroup()
    n = 3
    for k in range(n):
        angle = k * TAU / n
        tip = rotate_point(RIGHT * radius, angle)
        # zwei Basispunkte nahe der Mitte (dreieck)
        base1 = rotate_point(RIGHT * 0.3, angle + 0.5)
        base2 = rotate_point(RIGHT * 0.3, angle - 0.5)
        tri = Polygon(base1, tip, base2, stroke_width=2, fill_opacity=0.85, color=color)
        blades.add(tri)
    center = Dot([0, 0, 0], color=YELLOW)
    return blades, center


def perp_bisector_points(A, B, length=6):
    A = np.array(A);
    B = np.array(B)
    mid = (A + B) / 2
    v = B - A
    n = np.array([-v[1], v[0], 0])
    n = n / np.linalg.norm(n) * length
    return DashedLine(mid - n, mid + n, color=RED)


def intersection_point_of_segments(line1: Line, line2: Line):
    p1, p2 = line1.get_start_and_end()
    p3, p4 = line2.get_start_and_end()
    A = np.array([[p2[0] - p1[0], p3[0] - p4[0]], [p2[1] - p1[1], p3[1] - p4[1]]])
    b = np.array([p3[0] - p1[0], p3[1] - p1[1]])
    t, s = np.linalg.solve(A, b)
    return p1 + t * (p2 - p1)


from manim import *
import numpy as np

from manim import *
import numpy as np


# ---------- Progress Indicator (single object, updateable) ----------
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
            circ = Circle(radius=0.22, stroke_width=2, color=GRAY)
            circ.move_to([x, y, 0])
            self.circles.add(circ)
            num = Text(str(i + 1), font_size=16).move_to(circ.get_center())
            # labels ABOVE circles, smaller
            lbl = Text(sections[i], font_size=14, color=GRAY).next_to(circ, UP, buff=0.08)
            self.labels.add(lbl)
            self.add(circ, num, lbl)
            if i > 0:
                x_prev = -total_w / 2 + (i - 1) * spacing
                line = Line([x_prev + 0.22, y, 0], [x - 0.22, y, 0], stroke_width=3, color=GRAY)
                self.lines.add(line)
                self.add(line)

    def set_progress(self, idx):
        for i, circ in enumerate(self.circles):
            if i < idx:
                circ.set_fill(GREEN, 1)
                circ.set_stroke(GRAY, 2)
            elif i == idx:
                circ.set_fill(BLUE, 1)
                circ.set_stroke(GRAY, 2)
            else:
                circ.set_fill(None, 0)
                circ.set_stroke(GRAY, 1.5)
        for i, line in enumerate(self.lines):
            if i < idx - 0:
                line.set_color(GREEN)
            else:
                line.set_color(GRAY)


# ---------- Scene ----------
class DrehungenV5(Scene):
    def construct(self):
        config.tex_template.add_to_preamble(r"\usepackage{mathtools}")
        sections = ["Einstieg", "Definition", "Eigenschaften", "Drehung", "Bestimmung von Z, φ"]
        # progress bar appears AFTER title and with smaller labels above circles
        prog = ProgressBar(sections)
        self.play(FadeIn(prog))
        prog.set_progress(0)
        self.add(prog)

        # ---------- 1) Einstieg: centered windmill (3 triangular blades) ----------
        prog.set_progress(0)
        blades, center = make_windmill_three(radius=1.6, color=BLUE)
        mast = Line(DOWN * 3, center.get_center() + DOWN / 3, color=WHITE, stroke_width=12)
        self.play(FadeIn(mast), Create(blades), FadeIn(center))
        self.wait(0.5)
        self.play(Rotate(blades, angle=450 * DEGREES, about_point=center.get_center()), run_time=3)  # PI/2
        self.wait(0.5)
        self.play(FadeOut(mast), run_time=0.5)
        self.wait(0.5)

        # ---------- 2) Schreibweise ----------
        prog.set_progress(1)
        # choose top blade and its exact tip (so P is truly the blade-tip)
        tips = []
        for blade in blades:
            verts = blade.get_vertices()
            tip = max(verts, key=lambda v: v[1])
            tips.append((blade, tip))
        # pick blade with largest y tip (top blade)
        blade0, tip_coords = max(tips, key=lambda bt: bt[1][1])

        # Create copies for the "original" (left behind) elements:
        P_orig = Cross(Dot(tip_coords), stroke_width=2, stroke_color=BLUE)
        P_orig_label = MathTex("P").next_to(P_orig, RIGHT, buff=0.08)
        Z = Cross(center, stroke_width=3, stroke_color=YELLOW)  # nabe (Dot)
        Z_label = MathTex("Z").next_to(Z, DR, buff=0.08)
        line_orig = Line(Z.get_center(), P_orig.get_center(), color=BLUE)

        # Show originals (these remain in place)
        self.play(FadeIn(P_orig), Write(P_orig_label), Write(Z_label), Transform(center, Z))
        self.wait(0.5)

        # Now hide the full blades but keep a copy of the top blade we will transform later
        # Save the exact top-blade geometry to re-use as tri_orig
        tri_orig = blade0.copy()  # exact triangle of blade0
        # Hide all blades visually
        self.play(*[FadeOut(b) for b in blades], run_time=0.5)
        self.wait(0.5)
        self.play(Create(line_orig))
        self.wait(0.5)

        # Create moving copies that will rotate (these rotate around Z)
        P_move = P_orig.copy()
        P_move_label = P_orig_label.copy()
        line_move = line_orig.copy()
        self.add(P_move, P_move_label, line_move)  # add moving group

        # build arc path (only appears while P_move goes)
        phi1 = 90 * DEGREES
        ZP_len = np.linalg.norm(P_move.get_center() - Z.get_center())
        vec = P_move.get_center() - Z.get_center()
        start_angle = np.arctan2(vec[1], vec[0])
        arc1 = Arc(radius=ZP_len, start_angle=start_angle, angle=phi1, color=RED, stroke_width=4)
        phi_tex = MathTex(r"\varphi = 90^\circ", color=RED).next_to(arc1, RIGHT)

        tip = ArrowTriangleFilledTip(start_angle=-PI / 2, color=RED).scale(0.5)
        tip.move_to(arc1.point_from_proportion(1)).shift(UP * 0.1)

        # Animate arc creation and rotation of moving group simultaneously.
        # Rotating the line+point around Z keeps them linked.
        moving_group = VGroup(line_move, P_move, P_move_label)
        self.play(Create(arc1), Write(phi_tex), Rotate(moving_group, angle=phi1, about_point=Z.get_center()))
        self.wait(0.5)
        # After rotation, replace moving copies by final green P'
        Pp_pos = rotate_point(P_orig.get_center(), phi1, about=Z.get_center())
        Pp = Cross(Dot(Pp_pos), stroke_width=2, stroke_color=GREEN)
        Pp_label = MathTex("P'").next_to(Pp, LEFT, buff=0.05)
        # remove moving copies, keep originals too
        self.play(FadeOut(P_move, P_move_label), FadeIn(Pp), FadeIn(tip), Write(Pp_label),
                  FadeToColor(line_move, GREEN))
        self.wait(0.5)
        # show mapping notation
        notation = MathTex(r"P \xmapsto{Z;\ \varphi = 90^\circ} P'", color=ORANGE).scale(1.0).move_to(DOWN * 3)
        self.play(Write(notation))
        self.wait(0.5)

        # Now: bring back EXACT original top blade (tri_orig) and transform it to the image (no raw rotate animation)
        # Place tri_orig where it originally was (it already is), but ensure it's visible.
        # alte elemente entfernen
        self.play(FadeOut(notation, arc1, phi_tex, line_move, Pp, Pp_label, line_orig, tip), run_time=0.5)
        self.wait(0.5)

        tri_orig.move_to(tri_orig.get_center())  # ensure correct positioning
        self.play(FadeIn(tri_orig))
        self.wait(0.5)
        # Build the target (transformed) triangle by rotating tri_orig around Z by -120°
        phi2 = 120 * DEGREES
        # naming vertices: compute P,Q,R and P',Q',R' based on tri_orig and tri_target vertices
        verts_ur = tri_orig.get_vertices()
        Q_dot = Cross(Dot(verts_ur[0]), stroke_width=2, stroke_color=BLUE)
        R_dot = Cross(Dot(verts_ur[2]), stroke_width=2, stroke_color=BLUE)
        Q_label2 = MathTex("Q").next_to(Q_dot, UL, buff=0.04)
        R_label2 = MathTex("R").next_to(R_dot, UR, buff=0.04)

        # Transform tri_orig to tri_target (visually a transform, not a raw Rotate)
        self.play(FadeIn(Q_dot, R_dot), Write(Q_label2), Write(R_label2))
        self.play(FadeOut(Z_label), run_time=0.5)
        self.wait(0.5)

        # ROTATION
        tri_move = tri_orig.copy()
        P_move = P_orig.copy()
        Q_move = Q_dot.copy()
        R_move = R_dot.copy()
        moving_group = VGroup(tri_move, P_move, Q_move, R_move)

        self.play(Rotate(moving_group, angle=-phi2, about_point=Z.get_center()))
        self.wait(0.5)

        Pp_label2 = MathTex("P'").next_to(P_move, UR, buff=0.04)
        Qp_label2 = MathTex("Q'").next_to(Q_move, RIGHT, buff=0.04)
        Rp_label2 = MathTex("R'").next_to(R_move, DOWN, buff=0.04)
        self.play(FadeToColor(tri_move, GREEN), FadeToColor(P_move, GREEN), FadeToColor(Q_move, GREEN),
                  FadeToColor(R_move, GREEN), Write(Pp_label2),
                  Write(Qp_label2), Write(Rp_label2))
        self.wait(0.5)

        notation = MathTex(r"PQR \xmapsto{Z;\ \varphi = -120^\circ} P'Q'R'", color=ORANGE).scale(1.0).move_to(
            DOWN * 3)
        self.play(Write(notation))
        self.wait(0.5)
        self.play(FadeOut(P_move, Q_move, R_move, P_orig, R_dot, Q_dot, Z, Pp_label2, Qp_label2, Rp_label2, Q_label2,
                          R_label2, P_orig_label), run_time=0.5)
        self.wait(0.5)

        # Drehwinkel-Konventionen
        # --- Bögen nach unten + Pfeilspitzen ---
        left_arc = Arc(radius=0.8, start_angle=PI / 2, angle=PI / 2, color=ORANGE).next_to(P_orig, LEFT, buff=0.3)
        right_arc = Arc(radius=0.8, start_angle=PI / 2, angle=-PI / 2, color=ORANGE).next_to(P_orig, RIGHT, buff=0.3)

        # Pfeilspitzen: am jeweiligen Arc-Endpunkt, leicht verlängert nach unten
        left_tip = ArrowTriangleFilledTip(start_angle=-PI / 2, color=ORANGE).scale(0.5)
        right_tip = ArrowTriangleFilledTip(start_angle=-PI / 2, color=ORANGE).scale(0.5)

        # Positionieren: Arc-Endpunkte berechnen
        left_tip.move_to(left_arc.point_from_proportion(1))  # Ende des Bogens
        right_tip.move_to(right_arc.point_from_proportion(1))

        phi_left = MathTex(r"\varphi \ge 0", color=ORANGE).scale(0.9).next_to(left_arc, DOWN, buff=0.1)
        phi_right = MathTex(r"\varphi \le 0", color=ORANGE).scale(0.9).next_to(right_arc, DOWN, buff=0.1)

        self.play(Create(left_arc), Create(right_arc), FadeIn(left_tip), FadeIn(right_tip), Write(phi_left),
                  Write(phi_right))
        self.wait(0.5)

        # Ungleichungen verändern
        phi_left_new = MathTex(r"\varphi > 0", color=ORANGE).scale(0.9).move_to(phi_left)
        phi_right_new = MathTex(r"\varphi < 0", color=ORANGE).scale(0.9).move_to(phi_right)

        self.play(Transform(phi_left, phi_left_new), Transform(phi_right, phi_right_new))
        self.wait(0.5)
        self.play(FadeOut(left_arc, right_arc, left_tip, right_tip, phi_left_new, phi_right_new, phi_right, phi_left,
                          notation, Z, center), run_time=0.5)
        self.wait(0.5)

        # ---------- 3) Eigenschaften: (tri_orig is the image, tri_ur is the preimage) ----------
        prog.set_progress(2)

        self.play(tri_move.animate.rotate(120 * DEGREES, about_point=tri_move.get_center()))
        self.play(
            tri_orig.animate.move_to(ORIGIN + LEFT),
            tri_move.animate.move_to(ORIGIN + RIGHT))
        self.play(tri_orig.animate.move_to(ORIGIN), tri_move.animate.move_to(ORIGIN))
        self.play(FadeToColor(tri_orig, (GREEN + BLUE)), FadeToColor(tri_move, (GREEN + BLUE)))
        self.wait(0.5)

        kong_text = Text("Kongruenzabbildung: Urfigur und Bildfigur sind deckungsgleich", color=ORANGE,
                         font_size=28).move_to(DOWN * 3)
        self.play(Write(kong_text))
        self.wait(0.5)
        self.play(FadeOut(kong_text, tri_orig, tri_move), run_time=0.5)
        self.wait(0.5)

        # Fixpunkt: assemble full windmill centrally and rotate it; remove P',Q',R' first (as requested)
        prog.set_progress(2)
        wind_centered, center_dot = make_windmill_three(radius=1.6, color=BLUE)
        # wind_centered is a VGroup of triangles; center_dot is Dot
        self.play(Create(wind_centered), FadeIn(center_dot))
        self.wait(0.5)
        self.play(Rotate(wind_centered, angle=360 * DEGREES, about_point=center_dot.get_center()), run_time=2)
        self.wait(0.5)
        fix_text = Text("Drehzentrum Z ist einziger Fixpunkt", font_size=26, color=ORANGE).move_to(DOWN * 3)
        self.play(Write(fix_text))
        self.wait(0.5)

        # ---------- 4) Drehung durchführen ----------
        prog.set_progress(3)
        # clean up the items from (3) to avoid conflicts
        self.play(FadeOut(wind_centered, center_dot, fix_text), run_time=0.5)
        self.wait(0.5)

        plane = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-3, 4, 1],
            background_line_style={"stroke_color": GREY, "stroke_width": 1, "stroke_opacity": 0.35},
            axis_config={"stroke_color": GREY_B, "stroke_width": 2, "stroke_opacity": 0.8, "include_tip": True},
        ).add_coordinates(font_size=20, stroke_width=1, num_decimal_places=0).scale(0.95)
        self.play(Create(plane))
        self.wait(0.5)

        final_not = MathTex(r"P \xmapsto{Z;\ \varphi = 45^\circ} P'").scale(1.0).move_to(2 * RIGHT + 2 * DOWN)

        Z4 = Cross(Dot(plane.coords_to_point(0, 0)), stroke_width=2, stroke_color=YELLOW)
        P4 = Cross(Dot(plane.coords_to_point(2, 0)), stroke_width=2, stroke_color=BLUE)

        P4_label = MathTex("P (2|0)", color=BLUE).next_to(P4, DR, buff=0.08)
        Z4_label = MathTex("Z (0|0)", color=YELLOW).next_to(Z4, DL, buff=0.08)

        self.play(FadeIn(Z4), FadeIn(P4), Write(P4_label), Write(Z4_label), Write(final_not))
        self.wait(0.5)

        line_help = Line(Z4.get_center(), P4.get_center(), color=GREY)
        self.play(Create(line_help))
        self.wait(0.5)

        # helper line Z->P'
        P4p_pos = rotate_point(P4.get_center(), PI / 4, about=Z4.get_center())
        line_hint = Line(Z4.get_center(), P4p_pos, color=GRAY)
        self.play(Create(line_hint))
        self.wait(0.5)

        arc4 = ArcBetweenPoints(
            plane.coords_to_point(2, 0),
            plane.coords_to_point(2 * np.cos(PI / 4), 2 * np.sin(PI / 4)),
            radius=plane.x_axis.unit_size * 2,
            color=RED,
            stroke_width=4
        )
        self.play(Create(arc4))
        self.wait(0.5)

        P4p = Cross(Dot(rotate_point(P4.get_center(), PI / 4, about=Z4.get_center())), stroke_width=2,
                    stroke_color=GREEN)
        P4p_label = MathTex("P`", color=GREEN).next_to(P4p, UP, buff=0.08)
        self.play(FadeIn(P4p, P4p_label))
        self.wait(0.5)
        self.play(FadeOut(P4, P4p, P4p_label, Z4, arc4, line_hint, P4_label, Z4_label, final_not), run_time=0.5)
        self.wait(0.5)

        # ---------- 5) Bestimmung: Mittelsenkrechten + Kreissektoren ----------
        prog.set_progress(4)
        # clear these demo dots but keep axes
        Z_dot = Cross(Dot(plane.coords_to_point(0.5, -0.3)), stroke_width=2, stroke_color=YELLOW)
        Z_label = MathTex("Z", color=YELLOW).next_to(Z_dot, LEFT, buff=0.08)
        phi_val = 75 * DEGREES
        P5 = Cross(Dot(plane.coords_to_point(1, -0.5)), stroke_width=2, stroke_color=BLUE)
        Q5 = Cross(Dot(plane.coords_to_point(3, -1)), stroke_width=2, stroke_color=BLUE)
        R5 = Cross(Dot(plane.coords_to_point(3, 0)), stroke_width=2, stroke_color=BLUE)
        P5p_coords = rotate_point(P5.get_center(), phi_val, about=Z_dot.get_center())
        Q5p_coords = rotate_point(Q5.get_center(), phi_val, about=Z_dot.get_center())
        R5_coords = rotate_point(R5.get_center(), phi_val, about=Z_dot.get_center())
        P5p = Cross(Dot(P5p_coords), stroke_width=2, stroke_color=GREEN)
        Q5p = Cross(Dot(Q5p_coords), stroke_width=2, stroke_color=GREEN)
        R5p = Cross(Dot(R5_coords), stroke_width=2, stroke_color=GREEN)
        labels5 = VGroup(
            MathTex("P").next_to(P5, DOWN, buff=0.05),
            MathTex("P'").next_to(P5p, UR, buff=0.05),
            MathTex("Q").next_to(Q5, DL, buff=0.05),
            MathTex("Q'").next_to(Q5p, DR, buff=0.05),
            MathTex("R").next_to(R5, RIGHT, buff=0.05),
            MathTex("R'").next_to(R5p, UR, buff=0.05),
        )
        tri = Polygon(P5.get_center(), Q5.get_center(), R5.get_center(), color=BLUE, fill_opacity=0.4)
        trip = Polygon(P5p.get_center(), Q5p.get_center(), R5p.get_center(), color=GREEN, fill_opacity=0.4)
        self.play(FadeIn(P5, Q5, R5), FadeIn(P5p, Q5p, R5p), FadeIn(tri, trip), Write(labels5))
        self.wait(0.5)

        # Mittelsenkrechten
        pgroup = VGroup(P5, P5p)
        m1 = perp_bisector_points(P5.get_center(), P5p.get_center(), length=5)
        m2 = perp_bisector_points(R5.get_center(), R5p.get_center(), length=5)
        self.play(Indicate(pgroup, scale_factor=1.2, color=RED), Create(m1), run_time=0.5)
        self.wait(0.5)
        qgroup = VGroup(R5, R5p)
        self.play(Indicate(qgroup, scale_factor=1.2, color=RED), Create(m2), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(Z_dot), Write(Z_label))
        self.wait(0.5)

        tri_cooy = tri.copy()
        rot_group = VGroup(P5, Q5, R5).copy()
        rot_group.add(tri_cooy)
        self.play(Rotate(rot_group, about_point=Z_dot.get_center(), angle=phi_val))
        self.wait(0.5)
        self.play(FadeOut(rot_group), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(m1, m2), run_time=0.5)

        # phi ist dein Drehwinkel (z. B. PI/4) # Z und P sind Dots (Mobjects) # berechne Start- und Endwinkel (Z → P, Z → P')
        start_angle = Line(Z_dot.get_center(), Q5.get_center()).get_angle()
        end_angle = Line(Z_dot.get_center(),
                         Q5p.get_center()).get_angle()

        # gerichtete Differenz: von P -> P'
        angle_val = end_angle - start_angle

        # wenn der Bogen „rückwärts“ geht, auf 2π normalisieren
        if angle_val < 0:
            angle_val += 2 * PI

        # Radius = |ZP|
        r = np.linalg.norm(Q5.get_center() - Z_dot.get_center())

        # Kreisbogen (nicht gefüllt!)
        arc = Arc(radius=r, start_angle=start_angle, angle=angle_val, color=RED, stroke_width=3).move_arc_center_to(
            Z_dot.get_center())

        self.play(Create(arc))
        self.wait(2)

# manim -pqh .\drehungen.py DrehungenV5
