import mido
import rtmidi
from nicegui import app, ui
from collections import deque

class MidiMonitor():
    
    def __init__(self):
        # Use a 100 element ring buffer to keep track of items
        self.buffer = deque(maxlen=100)
        self.midiin = rtmidi.MidiIn()
        self.midiPorts = self.midiin.get_ports()
        self.isConnected = False

    # Connect to chosen midi port if not connected yet
    def connect(self, midi_port_name):
        
        if self.isConnected:
            ui.notify(f"Already connected to {self.connectedTo}")
            
        ui.notify(f"Trying to connect to: {midi_port_name}.....")
        
        try:
            self.midiin.open_port(self.midiin.get_ports().index("MIDIIN7 (ESI M4U eX) 6"))
            self.midiin.set_callback(lambda m, d: d.append(self.__parse(m)), data=self.buffer)
        except Exception as e:
            ui.notify(e)
        else:
            self.isConnected = True
            self.connectedTo = midi_port_name
            ui.notify("Connection Succesful")
    
    # Use mido to parse the MIDI message    
    def __parse(self, msg):
        try:
            parsed_value = mido.Message.from_bytes(msg[0])
            return str(parsed_value)
        except Exception as e:
            print(e)
        return msg
        
    # Disconnect, if connected
    def disconnect(self):
        if self.isConnected:
            self.midiin.close_port()
            self.isConnected = False
            self.connectedTo = None
            ui.notify("Disconnected")
        else:
            ui.notify("Not currently connected to a MIDI port")
    
    # Cleanup
    def __del__(self):
        self.midiin.close_port()
        del self.midiin

########################################################################

midiMonitor = MidiMonitor()

with ui.row():
    ui.select(options=midiMonitor.midiPorts, 
              label="Available MIDI Ports", 
              value=midiMonitor.midiPorts[0], 
              on_change=lambda e: app.storage.general.__setitem__('selectedMidiDevice', e.value))
    with ui.button_group():
        ui.button(text="Connect", on_click= lambda: midiMonitor.connect(app.storage.general['selectedMidiDevice']))
        ui.button(text="Disconnect", on_click=midiMonitor.disconnect)
    ui.label().bind_text_from(midiMonitor, 'isConncted', lambda v: 'Connected' if v == True else 'Not Connected')

with ui.row():  
    ui.html("div").bind_content_from(midiMonitor, 'buffer', lambda v: "<br>".join(list(v)[:50])).style("width: 400px; height: 1060px; border: 1px solid black; overflow-y: scroll")
    ui.html("div").bind_content_from(midiMonitor, 'buffer', lambda v: "<br>".join(list(v)[50:])).style("width: 400px; height: 1060px; border: 1px solid black; overflow-y: scroll")

with ui.button_group():
    ui.button('reset', on_click=app.reset)
    ui.button('shutdown', on_click=app.shutdown)
ui.run(reload=False)