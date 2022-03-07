__author__ = 'Christopher Collazo'
__email__ = 'christopher.collazof@outlook.com'
__status__ = 'Producción'
__version__ = '2.0.2'


from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.list import OneLineIconListItem, IconRightWidget, OneLineRightIconListItem
from kivymd.icon_definitions import md_icons
from kivy.uix.image import AsyncImage
from kivy.config import Config
from time import sleep
from subprocess import Popen, PIPE, STDOUT, CREATE_NO_WINDOW
from threading import Thread
from os import path


detener = True
rutas = []


def ffmpeg():
    
    global rutas
    sleep(.8)

    while detener:

        if len(rutas) > 0:
            archivo = rutas[0]
            nombre = path.basename(archivo)

            if MDApp.get_running_app().root.gif.source == 'GatitoFlojo.gif':
                MDApp.get_running_app().root.gif.source = 'GatitoActivo.gif'
                #MDApp.get_running_app().root.gif.reload()
            
            for element in MDApp.get_running_app().root.ids.lista.children:
                if element.text == nombre:
                    MDApp.get_running_app().root.ids.lista.remove_widget(element)
                    if len(MDApp.get_running_app().root.ids.lista.children) == 0:
                        MDApp.get_running_app().root.ids.lista.add_widget(Arrastrar())
                    break

            MDApp.get_running_app().root.ids.video.text = path.basename(archivo)
            info = 'ffmpeg -v info -i "%s"  ' % str(archivo)
            salida = Popen(info, stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=False, creationflags=CREATE_NO_WINDOW)

            for line in salida.stdout:

                if line.find('yuv420p10') != -1:
                    print(line)
                    luma_l = '65'
                    luma_h = '965'
                    break
                elif line.find('yuv420p') != -1:
                    print(line)
                    luma_l = '17'
                    luma_h = '235'
                    break

            s = 1
            duracion = 0
            name, ext = path.splitext(archivo)
            
            while path.exists(name + '.mxf'):
                name += '_' + str(s)
                s += 1

            comando = """ffmpeg -hwaccel auto -i "%s" -af "loudnorm=I=-24:LRA=14:tp=-6:measured_I=-30:measured_LRA=1.1:measured_tp=-11:measured_thresh=-40.21:offset=-0.47" -ac 2 -ar 48000  -vf "lutyuv='clip(val,%s,%s)',bwdif = mode = 1: parity = 0, scale=1440:1080, tinterlace = 4" -c:v libx264 -r 30000/1001 -g 1 -pix_fmt yuv420p10le -vb 50M -flags +ilme+ildct -tune psnr -color_range 2 -top 1 -avcintra-class 50 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -coder 0 "%s" """ % (archivo, luma_l, luma_h, name+'.mxf')
            salida = Popen(comando, stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=False, creationflags=CREATE_NO_WINDOW)
                                
            for line in salida.stdout:
                x = line.find('Duration: ')
                p = line.find('frame=')
                if x > -1:
                    duracion += int(line[x+10:x+12])*108000
                    duracion += int(line[x+13:x+15])*1800
                    duracion += int(line[x+16:x+18])*30
                elif p > -1:
                    f = line[p:].find('fps=')
                    c = int(line[p+6:f].replace(' ','',-1))
                    pp = (c*100)/duracion
                    MDApp.get_running_app().root.ids.progreso.value = pp
            
            MDApp.get_running_app().root.ids.progreso.value = 0
            MDApp.get_running_app().root.ids.video.text = ''
            rutas.remove(archivo)            
            
        else:

            try:
                if MDApp.get_running_app().root.ids.gif.source == 'GatitoActivo.gif':               
                    MDApp.get_running_app().root.ids.gif.source = 'GatitoFlojo.gif'
                    MDApp.get_running_app().root.ids.gif.reload()
                sleep(.5)
            except:
                sleep(.5)


ff = Thread(target=ffmpeg)
ff.start()

class Raiz(MDBoxLayout):
    pass

class Gato(AsyncImage):
    
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            MDApp.get_running_app().info()
        return super(Gato, self).on_touch_down(touch)

class Elemento(OneLineRightIconListItem):
    pass

class Arrastrar(MDLabel):
    pass

class Descarga(MDProgressBar):
    pass

class TranscodifiGator(MDApp):
    
    Config.set('kivy', 'window_icon', 'Gato.ico')
    Config.set('graphics', 'resizable',False)
    pantalla = ObjectProperty
    gif = ObjectProperty
    video = ObjectProperty
    progreso = ObjectProperty
    lista = ObjectProperty
    arras = '\n\n\n\n         Arrastra tus\n         videos aquí'
    dialog = None
    x = 0
    
    def __init__(self, **kwargs):
        Config.set('kivy', 'window_icon', 'Gato.ico')
        Window.size = (324,500)
        self.title = 'TranscodifiGator'
        self.icon = 'Gatito.ico'
        super(TranscodifiGator, self).__init__(**kwargs)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        Window.bind(on_dropfile=self._on_file_drop)
        self.root = Builder.load_file('main.kv')
        return self.root         

    def _on_file_drop(self, window, file_path):        
        global rutas
        if self.root.ids.lista.children[0].text == self.arras:
            self.root.ids.lista.remove_widget(self.root.ids.lista.children[0])
        archivo = file_path.decode(encoding='UTF-8')
        name, ext = path.splitext(archivo)
        nombre = path.basename(archivo)
        ext = ext.lower()

        if path.isfile(archivo) and (ext=='.mp4' or ext=='.mov' or ext=='.mxf' or ext=='.gxf' or ext=='.ts'):            
            self.root.ids.lista.add_widget(Elemento(text=nombre))
            rutas.append(archivo)
        
    def info(self):
        self.dialog = MDDialog(
                text="""Desarrollado por Christopher Collazo\n
                        christopher.collazof@outlook.com""",
                radius=[20, 7, 20, 7],
                buttons=[
                    MDFlatButton(
                        text="ACEPTAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=lambda _: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.open()

    def eliminar(self, padre):
        sleep(.1)
        buscar = padre.text
        n = len(buscar)
        self.root.ids.lista.remove_widget(padre)

        for archivo in rutas:
            if archivo[-n:] == buscar:
                rutas.remove(archivo)
    

    def on_stop(self):

        global detener
        detener = False


if __name__ == '__main__':
    TranscodifiGator().run()