from manim import *
import numpy as np

config.background_color = "#0e0e0e"


class Intro(Scene):
    def construct(self):
        # Mittelpunkt
        center = Dot(ORIGIN, color=YELLOW)
        self.add(center)

        # Radien
        R1 = 2.0  # Radius der äußeren Kreisbahn
        R2 = 0.8  # Radius der inneren Kreisbahn

        # Punkte
        p1 = Dot([0, R1, 0], color=BLUE)
        p2 = Dot([0, R1 + R2, 0], color=RED)
        self.add(p1, p2)

        # Tracker für die Winkel
        angle1 = ValueTracker(0)
        angle2 = ValueTracker(0)

        # Updater für p1 (rotierend um Zentrum)
        p1.add_updater(lambda m: m.move_to(
            ORIGIN + R1 * np.array([
                np.cos(angle1.get_value()),
                np.sin(angle1.get_value()), 0
            ])
        ))

        # Updater für p2 (rotierend um p1)
        p2.add_updater(lambda m: m.move_to(
            p1.get_center() + R2 * np.array([
                np.cos(angle2.get_value()),
                np.sin(angle2.get_value()), 0
            ])
        ))

        # Farbverlauf-Trail (Verlauf von Blau → Pink)
        trail = TracedPath(
            p2.get_center,
            stroke_color=[BLUE, PURPLE, PINK],
            stroke_width=5,
            dissipating_time=24  # ,   # langsam ausblenden, damit Verlauf bleibt
            # min_distance_to_new_point=0.01
        )

        self.add(trail)

        # Animation starten
        title = Text("Drehsymmetrische Figuren", color=YELLOW).scale(1.2).move_to(DOWN * 3)
        self.play(
            angle1.animate.set_value(2 * PI),
            angle2.animate.set_value(-8 * PI),  # schneller für "Doppelrotationseffekt"
            # Write(title),
            run_time=6.7,
            rate_func=linear
        )

        self.play(FadeOut(center, p1, p2))
        self.wait(0.5)
