# pyre-ignore-all-errors
class RebarDetailing:
    """Generates precise SVG vector strings for cross-sectional and elevation reinforcement drawings."""
    
    @staticmethod
    def generate_beam_cross_section(b: float, h: float, cover: float, top_bars: int, bot_bars: int, stirrup_dia: float) -> str:
        """
        Creates an SVG string representing a rectangular beam cross section with main bars and stirrups.
        """
        # Drawing scaling
        scale = 1.0 # SVG viewBox units
        svg_w = b * scale + 100
        svg_h = h * scale + 100
        shift_x = 50
        shift_y = 50
        
        svg = f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">\n'
        
        # Concrete outline
        svg += f'  <rect x="{shift_x}" y="{shift_y}" width="{b}" height="{h}" fill="#f0f0f0" stroke="#333" stroke-width="2"/>\n'
        
        # Stirrup
        s_x = shift_x + cover
        s_y = shift_y + cover
        s_w = b - 2*cover
        s_h = h - 2*cover
        svg += f'  <rect x="{s_x}" y="{s_y}" width="{s_w}" height="{s_h}" fill="none" stroke="#2563eb" stroke-width="{stirrup_dia}" rx="10" ry="10"/>\n'
        
        # Bars
        def draw_bars(num_bars, y_pos):
            if num_bars <= 0: return ""
            spacing = (s_w - 20) / (num_bars - 1) if num_bars > 1 else 0
            start_x = s_x + 10
            bar_svg = ""
            for i in range(num_bars):
                cx = start_x + i * spacing
                bar_svg += f'  <circle cx="{cx}" cy="{y_pos}" r="8" fill="#1e3a8a"/>\n'
            return bar_svg
            
        svg += draw_bars(top_bars, s_y + 10) # Top main bars
        svg += draw_bars(bot_bars, s_y + s_h - 10) # Bot main bars
        
        svg += '</svg>'
        return svg
