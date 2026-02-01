import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiMic, FiCheckCircle, FiAlertCircle, FiSend, FiUpload, FiVolume2, FiStopCircle, FiPhone, FiPhoneOff } from 'react-icons/fi';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [step, setStep] = useState('welcome'); // welcome, dialogue, summary
  const [claimId, setClaimId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0); // Temps d'enregistrement
  
  // État visible + refs de travail
  const [isFullCallUI, setIsFullCallUI] = useState(false);
  const [callActiveUI, setCallActiveUI] = useState(false);
  
  // ⭐ Utiliser des REFS au lieu d'états (pour éviter les closures JavaScript)
  const isFullCall = useRef(false);
  const callActive = useRef(false);
  
  const ws = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const recordingTimer = useRef(null); // Timer pour l'enregistrement auto

  const startConversation = async ({ preserveMode = false } = {}) => {
    // ⭐ Réinitialiser pour mode normal (pas d'appel)
    if (!preserveMode) {
      isFullCall.current = false;
      callActive.current = false;
      setIsFullCallUI(false);
      setCallActiveUI(false);
      console.log('🎙️ [SETUP] isFullCall=false, callActive=false (mode message)');
    }
    
    const sessionId = `session-${Date.now()}`;
    
    try {
      // Connexion WebSocket
      ws.current = new WebSocket(
        `ws://localhost:8000/ws/conversation/${sessionId}`
      );

      ws.current.onmessage = (event) => {
        console.log('📨 [BOT] Message reçu:', event.data.substring(0, 100));
        const data = JSON.parse(event.data);
        
          if (data.type === 'greeting') {
          console.log('👋 [BOT] GREETING reçu');
          setClaimId(data.claim_id);
          setMessages([{ speaker: 'system', text: data.message, hasAudio: !!data.audio_url, audioUrl: data.audio_url || null }]);
          setStep('dialogue');
          
          // En mode appel complet, démarrer l'enregistrement directement (pas de TTS)
          if (isFullCall.current && callActive.current) {
              console.log('🔊 [APPEL] Lecture audio ElevenLabs + enregistrement auto après');
              playAudio(data.audio_url, { autoRecord: true, fallbackText: data.message });
          } else {
            console.log('💬 [MESSAGE] Mode message, lecture audio');
            playAudio(data.audio_url, { fallbackText: data.message });
          }
        } else if (data.type === 'response') {
          console.log('💬 [BOT] RESPONSE reçue');
          let responseText = '';
          
          // Si c'est la première réponse après description (LAMA complet)
          if (data.acknowledge && data.summary) {
            responseText = `${data.acknowledge}\n\n${data.summary}\n\n${data.next_question || ''}`;
          } 
          // Si c'est une simple progression (collecte d'infos)
          else if (data.message) {
            responseText = data.message;
          }
          // Sinon juste la question
          else if (data.next_question) {
            responseText = data.next_question;
          }
          
          if (responseText) {
            console.log('📝 [BOT] Réponse texte:', responseText.substring(0, 80));
            setMessages(prev => [...prev, { speaker: 'system', text: responseText, hasAudio: !!data.audio_url, audioUrl: data.audio_url || null }]);
            
            // En mode appel, lecture TTS puis enregistrement auto
            if (isFullCall.current && callActive.current) {
              console.log('🔊 [APPEL] Lecture audio ElevenLabs + enregistrement auto après');
              playAudio(data.audio_url, { autoRecord: true, fallbackText: responseText });
            } else {
              console.log('💬 [MESSAGE] Mode message, lecture audio');
              playAudio(data.audio_url, { fallbackText: responseText });
            }
          }
          
          // Si conversation terminée
          if (data.completed) {
            console.log('✅ [BOT] Conversation TERMINÉE');
            setTimeout(() => {
              alert('✅ Déclaration complète! Votre dossier sera traité rapidement.');
            }, 2000);
          }
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Connection error:', error);
    }
  };

  const speakText = (text, { autoRecord = false } = {}) => {
    if (!text) return;

    // Utiliser Web Speech API pour TTS (fallback navigateur)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'fr-FR';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      if (autoRecord) {
        utterance.onend = () => {
          if (isFullCall.current && callActive.current) {
            console.log('🎙️ [APPEL] TTS terminé → startAutoRecording');
            startAutoRecording();
          }
        };
        utterance.onerror = () => {
          console.warn('⚠️ TTS erreur → fallback enregistrement');
          if (isFullCall.current && callActive.current) {
            setTimeout(() => startAutoRecording(), 500);
          }
        };
      }

      try {
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        console.log('🔊 TTS activé');
      } catch (e) {
        console.warn('⚠️ TTS non disponible');
        if (autoRecord && isFullCall.current && callActive.current) {
          setTimeout(() => startAutoRecording(), 500);
        }
      }
    } else if (autoRecord && isFullCall.current && callActive.current) {
      setTimeout(() => startAutoRecording(), 500);
    }
  };
  const normalizeAudioUrl = (audioUrl) => {
    if (!audioUrl) return null;
    if (audioUrl.startsWith('http://') || audioUrl.startsWith('https://')) {
      return audioUrl;
    }
    return `${API_BASE}${audioUrl}`;
  };

  const playAudio = (audioUrl, { autoRecord = false, fallbackText = '' } = {}) => {
    const finalUrl = normalizeAudioUrl(audioUrl);
    if (!finalUrl) {
      console.warn('⚠️ Pas d\'URL audio, fallback Web Speech');
      speakText(fallbackText || 'Message reçu du serveur', { autoRecord });
      return;
    }

    console.log('🎵 Lecture audio ElevenLabs:', finalUrl);
    
    const audio = new Audio(finalUrl);
    
    audio.onloadedmetadata = () => {
      console.log(`🎵 Audio chargé (${audio.duration.toFixed(2)}s)`);
    };
    
    audio.onended = () => {
      console.log('✅ Audio terminé');
      if (autoRecord) {
        console.log('🎙️ Auto-recording après audio');
        startAutoRecording();
      }
    };
    
    audio.onerror = (e) => {
      console.error('❌ Erreur audio:', e);
      console.warn('⚠️ Fallback Web Speech');
      speakText(fallbackText || 'Erreur audio', { autoRecord });
    };
    
    audio.play().catch(err => {
      console.error('❌ Impossible de jouer audio:', err);
      speakText(fallbackText || 'Impossible de jouer audio', { autoRecord });
    });
  };
  const startAutoRecording = async () => {
    try {
      console.log('🎤 [1] Demande accès microphone...');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('✅ [2] Microphone autorisé');
      
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        console.log('📦 [6] Données audio reçues');
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        console.log('⏹️ [7] Enregistrement arrêté, blob création');
        const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
        console.log(`📊 [8] Blob créé (${blob.size} bytes)`);
        stream.getTracks().forEach(track => track.stop());
        console.log('🔌 [9] Microphone désactivé');
        
        console.log('📤 [10] Envoi blob au traitement');
        processAudioBlob(blob);
        setRecordingTime(0);
      };

      mediaRecorder.current.start();
      console.log('▶️ [3] Enregistrement démarré');
      setRecordingTime(0);

      // Timer visuel
      let elapsed = 0;
      setRecordingTime(1);
      recordingTimer.current = setInterval(() => {
        elapsed++;
        setRecordingTime(elapsed);
        console.log(`⏱️ ${elapsed}/10s`);
        
        if (elapsed >= 10) {
          clearInterval(recordingTimer.current);
        }
      }, 1000);
      
      // Arrêt automatique après 10 secondes
      console.log('⏳ [4] Timeout 10s défini');
      setTimeout(() => {
        if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
          console.log('⏹️ [5] Arrêt auto après 10s');
          mediaRecorder.current.stop();
          if (recordingTimer.current) {
            clearInterval(recordingTimer.current);
          }
        }
      }, 10000);
      
    } catch (error) {
      console.error('❌ ERREUR Microphone:', error);
      alert('Erreur: ' + error.message);
    }
  };

  const startFullCall = async () => {
    // Demander permission microphone explicite
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop()); // Libérer immédiatement
      console.log('✅ Permission microphone accordée');
    } catch (error) {
      alert('Erreur: Permission microphone refusée. Autorisez le microphone pour utiliser l\'appel complet.');
      return;
    }
    
    // ⭐ Synchroniser refs + état UI
    isFullCall.current = true;
    callActive.current = true;
    setIsFullCallUI(true);
    setCallActiveUI(true);
    console.log('🎙️ [SETUP] isFullCall=true, callActive=true');
    
    startConversation({ preserveMode: true });
  };

  const endFullCall = () => {
    isFullCall.current = false;
    callActive.current = false;
    setIsFullCallUI(false);
    setCallActiveUI(false);
    setRecordingTime(0);
    
    if (recordingTimer.current) {
      clearInterval(recordingTimer.current);
    }
    
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }
    
    if (ws.current) {
      ws.current.send(JSON.stringify({ type: 'close' }));
      ws.current.close();
    }
    
    window.speechSynthesis.cancel();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        processAudioBlob(blob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Microphone error:', error);
      alert('Erreur: Impossible d\'accéder au microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const processAudioBlob = async (blob) => {
    console.log('🔄 [11] DÉBUT processAudioBlob');
    setLoading(true);
    
    try {
      // Envoyer l'audio au backend pour STT
      const formData = new FormData();
      formData.append('file', blob, 'recording.wav');
      
      console.log('📡 [12] Envoi au backend /api/transcribe');
      const response = await axios.post(`${API_BASE}/api/transcribe`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log('✅ [13] Réponse reçue du backend:', response.data);
      
      if (response.data.success) {
        const transcript = response.data.transcript;
        console.log('📝 [14] Transcription:', transcript);
        setInput(transcript);
        
        // Ajouter le message transcrit et l'envoyer automatiquement
        setMessages(prev => [...prev, { 
          speaker: 'client', 
          text: transcript,
          hasAudio: true 
        }]);
        
        console.log('📤 [15] Envoi transcription au WebSocket');
        // Envoyer au WebSocket
        if (ws.current?.readyState === WebSocket.OPEN) {
          console.log('✅ [16] WebSocket OPEN, envoi message');
          ws.current.send(JSON.stringify({
            type: 'user_text',
            text: transcript
          }));
        } else {
          console.error('❌ [16] WebSocket NOT OPEN (readyState=' + ws.current?.readyState + ')');
        }
      } else {
        console.error('❌ [13] Backend retourna success=false');
      }
      
      setLoading(false);
      console.log('✅ [17] FIN processAudioBlob');
    } catch (error) {
      console.error('❌ [12] ERREUR:', error);
      alert('Erreur de transcription audio. Détails console.');
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    
    try {
      // Transcription STT via backend
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_BASE}/api/transcribe`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.success) {
        const transcript = response.data.transcript;
        
        // Ajouter le message transcrit
        setMessages(prev => [...prev, { 
          speaker: 'client', 
          text: transcript,
          hasAudio: true 
        }]);
        
        // Envoyer au WebSocket
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({
            type: 'user_text',
            text: transcript
          }));
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Upload & transcription error:', error);
      alert('Erreur lors de la transcription du fichier');
      setLoading(false);
    }
  };

  const sendMessage = async (text = input) => {
    if (!text.trim()) return;

    // Ajouter message utilisateur
    setMessages(prev => [...prev, { speaker: 'client', text, hasAudio: false }]);
    setInput('');
    setLoading(true);

    try {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          type: 'user_text',
          text
        }));
      }
    } catch (error) {
      console.error('Send error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-700/50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">AssuraTech AI</h1>
            <p className="text-sm text-slate-400">Gestion Cognitive des Sinistres</p>
          </div>
          {claimId && (
            <div className="text-xs bg-slate-700/50 px-3 py-2 rounded-lg text-slate-300">
              {claimId}
            </div>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-12">
        {step === 'welcome' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="mb-12">
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity }}
                className="inline-block mb-6"
              >
                <div className="text-6xl">🎙️</div>
              </motion.div>
              <h2 className="text-5xl font-bold text-white mb-4">
                Déclaration de Sinistre
              </h2>
              <p className="text-xl text-slate-400 mb-8">
                Une expérience conversationnelle naturelle et rassurante
              </p>
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={startConversation}
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-blue-500/50 transition-shadow"
            >
              💬 Conversation par Messages
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={startFullCall}
              className="ml-4 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-green-500/50 transition-shadow flex items-center gap-2"
            >
              <FiPhone className="w-5 h-5" />
              📞 Appel Complet (Auto)
            </motion.button>

            {claimId && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={endFullCall}
                className="ml-4 px-8 py-4 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-red-500/50 transition-shadow flex items-center gap-2"
              >
                <FiPhoneOff className="w-5 h-5" />
                Raccrocher
              </motion.button>
            )}

            {/* Features */}
            <div className="grid grid-cols-3 gap-8 mt-16">
              {[
                { icon: '🎧', title: 'Dialogue Naturel', desc: 'Parlez comme avec un conseiller' },
                { icon: '🤖', title: 'IA Cognitive', desc: 'Analyse intelligente en temps réel' },
                { icon: '⚡', title: 'Résolution Rapide', desc: 'Décision en quelques minutes' }
              ].map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.2 }}
                  className="p-6 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-blue-500/50 transition-colors"
                >
                  <div className="text-4xl mb-3">{feature.icon}</div>
                  <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-slate-400">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {step === 'dialogue' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col h-[70vh]"
          >
            {/* Messages */}
            <div className="flex-1 overflow-y-auto mb-6 space-y-4">
              <AnimatePresence>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className={`flex ${msg.speaker === 'client' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-md px-4 py-3 rounded-lg ${
                        msg.speaker === 'client'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800 text-slate-100 border border-slate-700'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                      {msg.hasAudio && msg.speaker === 'system' && (
                        <button
                          onClick={() => playAudio(msg.audioUrl) }
                          className="mt-2 text-xs text-slate-400 hover:text-white flex items-center gap-1"
                        >
                          <FiVolume2 className="w-3 h-3" />
                          Réécouter
                        </button>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {loading && (
                <motion.div
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="flex gap-2 text-slate-400 justify-start"
                >
                  <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                </motion.div>
              )}
            </div>

            {/* Input Controls */}
            <div className="space-y-3">
              {/* Mode Appel Complet */}
              {isFullCallUI && (
                <div className="flex flex-col items-center mb-4 gap-3">
                  <motion.div
                    animate={{ scale: callActiveUI ? [1, 1.05, 1] : 1 }}
                    transition={{ duration: 2, repeat: callActiveUI ? Infinity : 0 }}
                    className={`px-8 py-4 rounded-full font-bold text-lg flex items-center gap-3 ${
                      callActiveUI
                        ? recordingTime > 0 ? 'bg-red-600 text-white' : 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-slate-400'
                    }`}
                  >
                    {callActiveUI ? (
                      <>
                        <FiPhone className={`w-6 h-6 ${recordingTime > 0 ? 'animate-pulse' : ''}`} />
                        {recordingTime > 0 
                          ? `🎤 PARLEZ MAINTENANT (${recordingTime}/10s)` 
                          : '🔊 Bot parle... Écoutez'}
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={endFullCall}
                          className="ml-4 px-4 py-2 bg-slate-900 hover:bg-black rounded-lg flex items-center gap-2"
                        >
                          <FiPhoneOff className="w-4 h-4" />
                          Raccrocher
                        </motion.button>
                      </>
                    ) : (
                      <>
                        <FiPhoneOff className="w-6 h-6" />
                        Appel terminé
                      </>
                    )}
                  </motion.div>
                  
                  {/* Barre de progression visuelle */}
                  {callActiveUI && recordingTime > 0 && (
                    <div className="w-full max-w-md">
                      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-red-500"
                          initial={{ width: '0%' }}
                          animate={{ width: `${(recordingTime / 10) * 100}%` }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Contrôles manuels (cachés en mode appel complet) */}
              {!isFullCallUI && (
                <>
                  {/* Audio Controls */}
                  <div className="flex gap-3 justify-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={loading}
                  className={`px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors ${
                    isRecording
                      ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {isRecording ? (
                    <>
                      <FiStopCircle className="w-5 h-5" />
                      Arrêter
                    </>
                  ) : (
                    <>
                      <FiMic className="w-5 h-5" />
                      Enregistrer
                    </>
                  )}
                </motion.button>

                <label className="cursor-pointer">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold flex items-center gap-2"
                  >
                    <FiUpload className="w-5 h-5" />
                    Upload Audio
                  </motion.div>
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Text Input */}
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Ou tapez votre message..."
                  className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 text-white rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => sendMessage()}
                  disabled={loading || !input.trim()}
                  className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <FiSend className="w-5 h-5" />
                </motion.button>
              </div>
                </>
              )}
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
