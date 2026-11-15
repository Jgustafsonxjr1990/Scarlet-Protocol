"""Qt SVG raster checks for fixed slot pitch, visible client insets and high DPI."""
from pathlib import Path
import tempfile
import numpy as np
from PIL import Image
from PySide6.QtGui import QGuiApplication
from PySide6.QtSvg import QSvgRenderer
from render_preview import render_frame, ROOT
from window_art import PRESETS, make_decoration


def main():
    app=QGuiApplication([])
    checked=0
    with tempfile.TemporaryDirectory(prefix='scarlet-slot-render-') as directory:
        work=Path(directory)
        for edition in (False,True):
            for profile,options in PRESETS.items():
                svg=work/'decor.svg'
                make_decoration(svg,edition,options['slots'],options['glow'],options['frame_width'])
                renderer=QSvgRenderer(str(svg))
                for prefix in ('decoration','decoration-inactive'):
                    for edge in ('left','right','top','bottom','topleft','topright','bottomleft','bottomright'):
                        bounds=renderer.boundsOnElement(prefix+'-'+edge)
                        assert abs(bounds.width()-24)<.001 and abs(bounds.height()-24)<.001,(edge,bounds)
                for size in ((240,160),(731,419),(1537,911)):
                    for prefix in ('decoration','decoration-inactive'):
                        png=work/'frame.png';render_frame(svg,png,size,prefix)
                        pixels=np.array(Image.open(png))
                        # Top and side tiles have identical 24px spacing at every window size.
                        assert np.array_equal(pixels[10:18,48:72],pixels[10:18,72:96])
                        assert np.array_equal(pixels[48:72,10:18],pixels[72:96,10:18])
                        # Details are inside the KWin-visible border, outside the client inset.
                        client_inset=10+options['frame_width']
                        edge=pixels[12:client_inset,48:96,:3].astype(int)
                        assert edge.max()-edge.min()>35
                        assert pixels[0,0,3]==0 and pixels[12,size[0]//2,3]==255
                        checked+=1
                png=work/'hidpi.png';render_frame(svg,png,(480,300),dpr=2)
                assert Image.open(png).size==(960,600)
    # New asymmetric Obsidian tiles use 96px repeated edge bands and a taller header.
    with tempfile.TemporaryDirectory(prefix='scarlet-obsidian-render-') as directory:
        png=Path(directory)/'frame.png'
        for name in ('ScarletProtocolGlobal81','ScarletProtocolNight81'):
            source=ROOT/'aurorae'/name/'decoration.svg'
            for size in ((280,220),(731,419),(1537,911)):
                for prefix in ('decoration','decoration-inactive'):
                    render_frame(source,png,size,prefix)
                    pixels=np.array(Image.open(png))
                    assert np.array_equal(pixels[64:160,13:24],pixels[160:256,13:24]) if size[1]>300 else True
                    assert pixels[0,0,3]==0
                    assert pixels[20,size[0]//2,3]==255
                    assert pixels[65:-32,12:24,:3].max()>90
                    checked+=1
            render_frame(source,png,(480,300),dpr=2)
            assert Image.open(png).size==(960,600)
    print(f'PASS: {checked} Qt SVG frames across three sizes, both focus states, all profiles and editions; 2x DPI renders')


if __name__=='__main__': main()
