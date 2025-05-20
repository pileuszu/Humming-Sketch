import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class Note:
    pitch: int  # MIDI 노트 번호
    start_time: float  # 시작 시간 (초)
    end_time: float  # 종료 시간 (초)
    velocity: int  # MIDI 벨로시티 (1-127)

class NoteDetector:
    def __init__(self, 
                 hop_length=512,
                 sr=44100,
                 min_note_length=0.1,  # 최소 음표 길이 (초)
                 silence_threshold=0.3):  # 무음 임계값
        """
        음표 검출기 초기화
        
        Args:
            hop_length (int): STFT 프레임 간 홉 길이
            sr (int): 샘플링 레이트
            min_note_length (float): 최소 음표 길이 (초)
            silence_threshold (float): 무음으로 판단할 신뢰도 임계값
        """
        self.hop_length = hop_length
        self.sr = sr
        self.min_note_length = min_note_length
        self.silence_threshold = silence_threshold
        
    def _frames_to_time(self, frames):
        """프레임 수를 시간(초)으로 변환"""
        return frames * self.hop_length / self.sr
    
    def detect_notes(self, midi_notes: np.ndarray, confidence: np.ndarray) -> List[Note]:
        """
        MIDI 노트 시퀀스에서 개별 음표 검출
        
        Args:
            midi_notes (np.ndarray): MIDI 노트 시퀀스
            confidence (np.ndarray): 각 노트의 신뢰도
            
        Returns:
            List[Note]: 검출된 음표 리스트
        """
        notes = []
        current_note = None
        note_start_frame = 0
        
        for frame, (note, conf) in enumerate(zip(midi_notes, confidence)):
            # 현재 프레임이 무음인지 확인
            is_silence = conf < self.silence_threshold
            
            if current_note is None:
                if not is_silence:
                    # 새로운 음표 시작
                    current_note = note
                    note_start_frame = frame
            else:
                if is_silence or note != current_note:
                    # 현재 음표 종료
                    duration = frame - note_start_frame
                    if self._frames_to_time(duration) >= self.min_note_length:
                        notes.append(Note(
                            pitch=int(current_note),
                            start_time=self._frames_to_time(note_start_frame),
                            end_time=self._frames_to_time(frame),
                            velocity=min(127, max(1, int(100 * np.mean(confidence[note_start_frame:frame]))))
                        ))
                    
                    if not is_silence:
                        # 새로운 음표 시작
                        current_note = note
                        note_start_frame = frame
                    else:
                        current_note = None
        
        # 마지막 음표 처리
        if current_note is not None:
            duration = len(midi_notes) - note_start_frame
            if self._frames_to_time(duration) >= self.min_note_length:
                notes.append(Note(
                    pitch=int(current_note),
                    start_time=self._frames_to_time(note_start_frame),
                    end_time=self._frames_to_time(len(midi_notes)),
                    velocity=min(127, max(1, int(100 * np.mean(confidence[note_start_frame:]))))
                ))
        
        return notes
    
    def quantize_notes(self, notes: List[Note], tempo: float = 120.0, grid: float = 0.25) -> List[Note]:
        """
        음표의 시작/종료 시간을 그리드에 맞춰 양자화
        
        Args:
            notes (List[Note]): 음표 리스트
            tempo (float): 템포 (BPM)
            grid (float): 그리드 크기 (1.0 = 4분음표)
            
        Returns:
            List[Note]: 양자화된 음표 리스트
        """
        beat_length = 60.0 / tempo  # 한 비트(4분음표)의 길이(초)
        grid_length = beat_length * grid  # 그리드 간격(초)
        
        quantized_notes = []
        for note in notes:
            # 시작/종료 시간을 가장 가까운 그리드로 반올림
            start_grid = round(note.start_time / grid_length)
            end_grid = round(note.end_time / grid_length)
            
            # 최소 1개 그리드 이상 되도록 보정
            if start_grid == end_grid:
                end_grid = start_grid + 1
                
            quantized_notes.append(Note(
                pitch=note.pitch,
                start_time=start_grid * grid_length,
                end_time=end_grid * grid_length,
                velocity=note.velocity
            ))
            
        return quantized_notes 