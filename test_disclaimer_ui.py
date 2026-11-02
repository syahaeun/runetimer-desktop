"""Exercise disclaimer bounds and native owner modality with real Tk windows."""
import unittest
from unittest.mock import patch

# Reuse the isolated settings fixture; never read or change the user's profile.
from test_booster_ui import pc_app


class DisclaimerUITests(unittest.TestCase):
    def test_small_monitor_and_owner_modality(self):
        with patch.object(pc_app.PcTimerApp, '_show_startup_splash'):
            app = pc_app.PcTimerApp()
        try:
            app._show_main_window(force_focus=True)
            app._show_page('settings')
            app.root.update()
            with patch.object(app, '_disclaimer_work_area', return_value=(0, 0, 1024, 728)):
                app._show_disclaimer_dialog(readonly=True)
            app.root.update()
            dialog = app.disclaimer_dialog
            self.assertGreaterEqual(dialog.winfo_x(), 0)
            self.assertGreaterEqual(dialog.winfo_y(), 0)
            self.assertLessEqual(dialog.winfo_x() + dialog.winfo_width(), 1024)
            self.assertLessEqual(dialog.winfo_y() + dialog.winfo_height(), 728)
            self.assertEqual(app.root.grab_current(), dialog)
            self.assertTrue(app.root.attributes('-disabled'))
            app._keep_visible_tick()
            app._show_main_window(force_focus=True)
            app._force_main_window_visible(force_focus=True)
            app.root.update()
            self.assertFalse(app.root.attributes('-topmost'))
            self.assertTrue(dialog.attributes('-topmost'))
            self.assertTrue(app.root.attributes('-disabled'))
            self.assertEqual(dialog.cget('bg'), app.colors['surface'])
            self.assertEqual(dialog.attributes('-transparentcolor'), '')
            buttons = []

            def collect(widget):
                if isinstance(widget, pc_app.base.RoundedButton):
                    buttons.append(widget)
                for child in widget.winfo_children():
                    collect(child)

            collect(dialog)
            self.assertEqual(len(buttons), 1)
            button = buttons[0]
            self.assertTrue(button.winfo_ismapped())
            self.assertLessEqual(button.winfo_rooty() + button.winfo_height(),
                                 dialog.winfo_rooty() + dialog.winfo_height())
            # Invoke the actual window-manager close callback.
            dialog.tk.call(dialog.protocol('WM_DELETE_WINDOW'))
            app.root.update()
            self.assertIsNone(app.disclaimer_dialog)
            self.assertFalse(app.root.attributes('-disabled'))
            self.assertEqual(app.current_page, 'settings')
        finally:
            app.root.destroy()


if __name__ == '__main__':
    unittest.main()
