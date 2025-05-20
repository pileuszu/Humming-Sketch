import numpy as np
import librosa
from scipy.signal import medfilt

class PitchDetector:
    def __init__(self, sr=44100, hop_length=512, fmin=50, fmax=2000):
        """
        피치 검출기 초기화
        
        Args:
            sr (int): 샘플링 레이트
            hop_length (int): STFT 프레임 간 홉 길이
            fmin (float): 최소 주파수
            fmax (float): 최대 주파수
        """
        self.sr = sr
        self.hop_length = hop_length
        self.fmin = fmin
        self.fmax = fmax
    
    def detect_pitch(self, audio_data):
        """
        오디오 데이터에서 피치를 검출
        
        Args:
            audio_data (np.ndarray): 오디오 데이터
            
        Returns:
            tuple: (피치 시퀀스, 피치 신뢰도)
        """
        # YIN 알고리즘을 사용한 피치 검출
        pitches, magnitudes = librosa.piptrack(
            y=audio_data,
            sr=self.sr,
            hop_length=self.hop_length,
            fmin=self.fmin,
            fmax=self.fmax
        )
        
        # 각 프레임에서 가장 강한 피치 선택
        pitch_sequence = []
        confidence = []
        
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch_sequence.append(pitches[index, t])
            confidence.append(magnitudes[index, t])
            
        pitch_sequence = np.array(pitch_sequence)
        confidence = np.array(confidence)
        
        # 중앙값 필터로 노이즈 제거
        pitch_sequence = medfilt(pitch_sequence, kernel_size=5)
        
        return pitch_sequence, confidence
    
    def hz_to_midi(self, frequencies):
        """
        주파수(Hz)를 MIDI 노트 번호로 변환
        
        Args:
            frequencies (np.ndarray): 주파수 배열
            
        Returns:
            np.ndarray: MIDI 노트 번호 배열
        """
        # 0Hz (무음) 처리
        frequencies = np.where(frequencies > 0, frequencies, 0.1)
        
        # MIDI 노트 번호 계산: MIDI 노트 = 12 * log2(Hz/440) + 69
        midi_notes = 12 * np.log2(frequencies / 440.0) + 69
        
        # 가장 가까운 정수로 반올림
        midi_notes = np.round(midi_notes)
        
        return midi_notes
    
    def get_midi_notes(self, audio_data):
        """
        오디오 데이터에서 MIDI 노트 시퀀스 추출
        
        Args:
            audio_data (np.ndarray): 오디오 데이터
            
        Returns:
            tuple: (MIDI 노트 시퀀스, 신뢰도)
        """
        pitch_sequence, confidence = self.detect_pitch(audio_data)
        midi_notes = self.hz_to_midi(pitch_sequence)
        
        return midi_notes, confidence 