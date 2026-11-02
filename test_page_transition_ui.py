"""Verify page transitions cover the outgoing page and finish consistently."""
import time
import unittest
from unittest.mock import patch

from test_booster_ui import pc_app


class PageTransitionUITests(unittest.TestCase):
    def close_app(self, app):
        for callback in app.root.tk.call('after', 'info'):
            app.root.after_cancel(callback)
        app.root.destroy()

    def test_back_transition_order_and_repeated_click(self):
        with patch.object(pc_app.PcTimerApp, '_show_startup_splash'):
            app = pc_app.PcTimerApp()
        try:
            app._show_main_window(force_focus=True)
            app._show_page('settings')
            app.root.update()
            calls = []
            capture = app._capture_restore_blur_image
            overlay = app._show_restore_blur_overlay
            show = app._show_page

            def record_capture():
                calls.append(('capture', app.current_page))
                capture()

            def record_overlay(**kwargs):
                calls.append(('overlay', app.current_page))
                overlay(**kwargs)

            def record_show(name):
                calls.append(('page', name))
                show(name)

            with patch.object(app, '_capture_restore_blur_image', record_capture), \
                    patch.object(app, '_show_restore_blur_overlay', record_overlay), \
                    patch.object(app, '_show_page', record_show):
                app._switch_page_with_blur('monitor')
                app._switch_page_with_blur('settings')
            self.assertEqual(calls, [('capture', 'settings'), ('overlay', 'settings'), ('page', 'monitor')])
            self.assertTrue(app.page_transition_active)
            deadline = time.monotonic() + 2
            while app.page_transition_active and time.monotonic() < deadline:
                app.root.update()
                time.sleep(0.01)
            self.assertFalse(app.page_transition_active)
            self.assertIsNone(app.restore_blur_overlay)
            self.assertEqual(app.current_page, 'monitor')
        finally:
            self.close_app(app)

    def test_old_fade_cannot_remove_new_overlay(self):
        with patch.object(pc_app.PcTimerApp, '_show_startup_splash'):
            app = pc_app.PcTimerApp()
        try:
            app._show_main_window()
            app.root.update()
            app._show_restore_blur_overlay(hold_ms=10000)
            old = app.restore_blur_overlay
            app._show_restore_blur_overlay(hold_ms=10000)
            current = app.restore_blur_overlay
            app._fade_restore_blur_overlay(0.96, old, time.monotonic() - 1)
            self.assertIs(app.restore_blur_overlay, current)
            app._fade_restore_blur_overlay(0.96, current, time.monotonic() - 1)
            self.assertIsNone(app.restore_blur_overlay)
        finally:
            self.close_app(app)


if __name__ == '__main__':
    unittest.main()
