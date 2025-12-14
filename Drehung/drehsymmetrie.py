from manim import *
import numpy as np

# ---------- Config ----------
config.background_color = "#0e0e0e"


# ---------- Helpers ----------
def rotate_point(pt, angle, about=(0, 0, 0)):
    pt = np.array(pt, dtype=float)
    if pt.shape[0] == 2:
        pt = np.array([pt[0], pt[1], 0.0])
    about = np.array(about, dtype=float)
    if about.shape[0] == 2:
        about = np.array([about[0], about[1], 0.0])
    v = pt - about
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s], [s, c]])
    v2 = R @ v[:2]
    return np.array([v2[0], v2[1], 0.0]) + about


def make_windmill_three(radius=1.6, color=BLUE, fill_opacity=0.85):
    blades = VGroup()
    n = 3
    for k in range(n):
        angle = k * TAU / n
        tip = rotate_point(RIGHT * radius, angle)
        base1 = rotate_point(RIGHT * 0.3, angle + 0.5)
        base2 = rotate_point(RIGHT * 0.3, angle - 0.5)
        tri = Polygon(base1, tip, base2, stroke_width=2, fill_opacity=fill_opacity, color=color)
        blades.add(tri)
    center = Cross(Dot([0, 0, 0]), stroke_color=YELLOW, stroke_width=3)
    return blades, center


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
            line.set_color(GREEN if i < idx else GRAY)


# ---------- Scene ----------
class DrehsymmetrieV2(Scene):
    def construct(self):
        # Progressbar
        prog = ProgressBar(["Windrad", "Quadrat"])
        self.play(FadeIn(prog))
        prog.set_progress(0)
        self.add(prog)

        # --- phi Anzeige helper ---
        phi_tracker = ValueTracker(0)  # radians

        def phi_tex_updater(m: MathTex):
            deg = int(np.round(np.degrees(phi_tracker.get_value())))
            m.become(MathTex(r"\varphi = " + f"{deg}^\circ", color=RED).scale(0.7)
                     .move_to(DOWN * 2).shift(LEFT * 0.2 + DOWN * 0.2))

        phi_display = MathTex("").scale(0.7).to_corner(UR)
        phi_display.add_updater(lambda m: phi_tex_updater(m))
        self.add(phi_display)

        # ---------------- Scene 1: Windrad ----------------
        prog.set_progress(0)
        blades, center = make_windmill_three(radius=1.8, color=BLUE, fill_opacity=0.7)
        blades_green = blades.copy().set_color(GREEN)

        # Tips as points
        P = Cross(Dot(blades[0].get_vertices()[1]), stroke_color=BLUE, stroke_width=3)
        P_label = MathTex("P").next_to(P, UP)

        P_copy = P.copy().set_color(GREEN)
        P_label_copy = MathTex("P'").next_to(P, DOWN)

        # place both (base blue semi-transparent kept), green copy will rotate
        self.play(Create(blades), FadeIn(center, P, P_copy), FadeIn(blades_green.set_opacity(1.0)),
                  Write(P_label), Write(P_label_copy))
        # position phi tracker at 0
        phi_tracker.set_value(0)
        rot_group = VGroup(blades_green, P_copy, P_label_copy)

        # function to animate rotation to target degrees (in degrees), with optional flash
        # Funktion innerhalb von construct ersetzen
        def rotate_to(deg_target, run_time=1, flash=False):
            target_rad = deg_target * DEGREES
            # relativer Winkel = Differenz zum aktuellen phi_tracker
            delta = target_rad - phi_tracker.get_value()
            self.play(
                phi_tracker.animate.set_value(target_rad), # todo ausblenden mgl
                Rotate(rot_group, angle=delta, about_point=center.get_center()),
                run_time=run_time
            )
            self.play(Rotate(P_label_copy, angle=-delta, about_point=P_label_copy.get_center()), run_time=0.5)
            if flash:
                self.play(
                    *[obj.animate.set_fill(WHITE, 1) for obj in blades_green],
                    run_time=0.12
                )
                self.play(
                    *[obj.animate.set_fill(GREEN, 1) for obj in blades_green],
                    run_time=0.12
                )

        # rotate in steps: 120, flash, 240, flash, 360
        rotate_to(120, run_time=1.5, flash=True)
        rotate_to(240, run_time=1.5, flash=True)
        rotate_to(360, run_time=1.5, flash=False)
        self.wait(0.5)

        # short text note on minimal angle
        note1 = Text("Drehsymmetrie: Figur wird durch Drehung um ein φ≠360°\nauf sich selbst abgebildet", color=ORANGE,
                     font_size=28).move_to(DOWN * 3)
        self.play(Write(note1))
        self.wait(0.9)
        self.play(FadeOut(note1), run_time=0.5)
        # fade green a bit to show both
        self.play(FadeToColor(blades, BLUE), FadeToColor(blades_green, GREEN))

        # keep both for a beat then clear for next scene (but keep progress)
        self.wait(0.5)
        self.play(FadeOut(blades_green, blades, center, P, P_label, rot_group), run_time=0.5)
        phi_tracker.set_value(0)

        # ---------- 2) Quadrat (Drehsymmetrie & Punktsymmetrie) ----------
        prog.set_progress(1)

        # Quadrat erstellen
        square_blue = Square(side_length=2.4, color=BLUE, fill_opacity=0.6).move_to(ORIGIN)
        square_green = square_blue.copy().set_fill(GREEN, 0.6)
        Z = Cross(Dot(ORIGIN), stroke_width=3, stroke_color=YELLOW)

        P = Cross(Dot(square_blue.get_vertices()[0]), stroke_color=BLUE, stroke_width=3)
        P_label = MathTex("P").next_to(P, UP)
        P_copy = P.copy().set_color(GREEN)
        P_label_copy = MathTex("P'").next_to(P, RIGHT)
        rot_group = VGroup(P_copy, P_label_copy, square_green)

        self.play(Create(square_blue), FadeIn(Z, P, P_copy), Write(P_label), Write(P_label_copy))

        def rotate_to(deg_target, run_time=1, flash=False):
            """Hilfsfunktion für Rotationsanimationen mit optionalem Aufblitzen"""
            target_rad = deg_target * DEGREES
            self.play(
                phi_tracker.animate.set_value(target_rad), # Todo ausblenden mgl
                Rotate(rot_group, angle=(deg_target - np.degrees(phi_tracker.get_value())) * DEGREES,
                       about_point=Z.get_center()),
                run_time=run_time
            )
            self.play(Rotate(P_label_copy, angle=-PI/2,
                             about_point=P_label_copy.get_center()), run_time=0.1)
            if flash:
                # kurzes Weiß-Aufblitzen
                self.play(square_green.animate.set_fill(WHITE, 1), run_time=0.1)
                self.play(square_green.animate.set_fill(GREEN, 0.6), run_time=0.1)

        self.add(square_green)

        # Rotationen und Hervorhebungen
        rotate_to(90)
        self.wait(0.5)
        rotate_to(180, flash=True)

        punk_text = Text("Punktsymmetrie = Drehsymmetrie für φ=180°", color=ORANGE, font_size=26).move_to(DOWN * 3)
        self.play(Write(punk_text))

        rotate_to(270)
        self.wait(0.5)
        rotate_to(360)
        self.wait(2)
