from midiutil import MIDIFile
from typing import List
from .note_detection import Note

class MIDIConverter:
    def __init__(self, tempo: float = 120.0):
        """
        MIDI 변환기 초기화
        
        Args:
            tempo (float): 템포 (BPM)
        """
        self.tempo = tempo
        
    def notes_to_midi(self, notes: List[Note], output_file: str):
        """
        음표 리스트를 MIDI 파일로 변환
        
        Args:
            notes (List[Note]): 음표 리스트
            output_file (str): 출력 MIDI 파일 경로
        """
        # MIDI 파일 생성 (1개 트랙)
        midi = MIDIFile(1)
        track = 0
        time = 0
        
        # 트랙 초기화
        midi.addTrackName(track, time, "Humming")
        midi.addTempo(track, time, self.tempo)
        
        # 음표 추가
        for note in notes:
            # 시간을 박자 단위로 변환 (초 -> 박자)
            start_beat = note.start_time / (60.0 / self.tempo)
            duration = (note.end_time - note.start_time) / (60.0 / self.tempo)
            
            # 노트 이벤트 추가
            midi.addNote(
                track=track,
                channel=0,
                pitch=note.pitch,
                time=start_beat,
                duration=duration,
                volume=note.velocity
            )
        
        # MIDI 파일 저장
        with open(output_file, "wb") as f:
            midi.writeFile(f) 