// Eu Viro Voto App - Frontend Logic com Rastreamento Google Analytics 4 (G-JGEYVZG1ZB)

let deferredPrompt = null;
let mediaRecorder = null;
let audioChunks = [];
let recordedAudioBase64 = null;
let isRecording = false;
let lastSubmittedQuestion = "";
let inputMethodUsed = "texto";

// Helper universal de envio de eventos para o Google Analytics 4
function trackGA(eventName, params = {}) {
  if (typeof window.gtag === 'function') {
    try {
      // Limpa e sanitiza parâmetros para garantir compatibilidade com GA4
      const safeParams = {};
      for (const [key, val] of Object.entries(params)) {
        if (typeof val === 'string') {
          // Limita strings para até 300 caracteres para evitar truncamento no GA4
          safeParams[key] = val.slice(0, 300);
        } else {
          safeParams[key] = val;
        }
      }
      window.gtag('event', eventName, safeParams);
    } catch (err) {
      console.warn('[GA4] Falha ao enviar evento:', eventName, err);
    }
  }
}

// 1. Registro de Service Worker para PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((err) => {
      console.log('SW registration failed:', err);
    });
  });
}

// 2. Manipulador de Instalação PWA
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const banner = document.getElementById('installBanner');
  if (banner) banner.style.display = 'flex';
  trackGA('pwa_banner_exibido');
});

const installBtn = document.getElementById('installBtn');
if (installBtn) {
  installBtn.addEventListener('click', async () => {
    if (deferredPrompt) {
      trackGA('pwa_clique_instalar');
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      trackGA('pwa_instalacao_resultado', { resultado: outcome });
      if (outcome === 'accepted') {
        document.getElementById('installBanner').style.display = 'none';
      }
      deferredPrompt = null;
    }
  });
}

// 3. Preenchimento de exemplos rápidos
function fillSample(text) {
  const input = document.getElementById('userInput');
  input.value = text;
  input.focus();
  input.scrollIntoView({ behavior: 'smooth', block: 'center' });
  inputMethodUsed = "exemplo_clicado";

  // Rastreia no Google Analytics qual exemplo foi acionado
  trackGA('exemplo_clicado', {
    texto_exemplo: text
  });
}

// 4. Gravação de Áudio via Navegador
async function toggleAudioRecording() {
  const btn = document.getElementById('recordAudioBtn');
  const btnText = document.getElementById('recordBtnText');
  const micIcon = document.getElementById('micIcon');
  const statusText = document.getElementById('audioStatusText');

  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/ogg; codecs=opus' });
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
          recordedAudioBase64 = reader.result;
          inputMethodUsed = "audio_gravado";
          statusText.textContent = 'Áudio gravado pronto! ✓';
          statusText.style.color = '#00a884';

          trackGA('audio_gravacao_concluida', {
            tamanho_bytes: audioBlob.size
          });
        };
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      isRecording = true;
      btn.classList.add('recording');
      btnText.textContent = 'Parar';
      micIcon.textContent = '⏹️';
      statusText.textContent = 'Gravando sua voz...';
      statusText.style.color = '#ef4444';

      trackGA('audio_gravacao_iniciada');
    } catch (err) {
      alert('Não foi possível acessar o microfone. Permita o microfone no navegador.');
      trackGA('audio_gravacao_negada', { erro: err.message });
    }
  } else {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    isRecording = false;
    btn.classList.remove('recording');
    btnText.textContent = 'Gravar';
    micIcon.textContent = '🎙️';
  }
}

// 5. Upload de arquivo de áudio
function handleAudioFile(event) {
  const file = event.target.files[0];
  const statusText = document.getElementById('audioStatusText');
  if (!file) return;

  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onloadend = () => {
    recordedAudioBase64 = reader.result;
    inputMethodUsed = "arquivo_audio";
    statusText.textContent = `Áudio (${file.name.slice(0, 15)}...) pronto! ✓`;
    statusText.style.color = '#00a884';

    trackGA('audio_arquivo_selecionado', {
      nome_arquivo: file.name,
      tamanho_bytes: file.size,
      formato: file.type
    });
  };
}

// 6. Submissão para análise cognitiva
async function submitAnalysis() {
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  const submitBtn = document.getElementById('submitBtn');
  const loadingBox = document.getElementById('loadingBox');
  const resultsWrapper = document.getElementById('resultsWrapper');

  if (!text && !recordedAudioBase64) {
    showToast('Por favor, digite uma mensagem ou grave um áudio.');
    input.focus();
    return;
  }

  lastSubmittedQuestion = text || "[Áudio gravado/encaminhado]";

  // Rastreia o evento principal: PERGUNTA ENVIADA
  trackGA('pergunta_enviada', {
    pergunta: lastSubmittedQuestion,
    metodo_entrada: recordedAudioBase64 && text ? 'texto_e_audio' : (recordedAudioBase64 ? 'apenas_audio' : inputMethodUsed),
    tamanho_caracteres: text.length,
    tem_audio: Boolean(recordedAudioBase64)
  });

  // UI state: Carregando
  submitBtn.disabled = true;
  loadingBox.style.display = 'block';
  resultsWrapper.style.display = 'none';
  loadingBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

  const startTime = performance.now();

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        audio_base64: recordedAudioBase64
      })
    });

    const resData = await response.json();
    const result = (resData && resData.data) ? resData.data : resData;
    const durationMs = Math.round(performance.now() - startTime);

    // Rastreia o evento principal: VEREDITO GERADO
    trackGA('veredito_gerado', {
      pergunta_origem: lastSubmittedQuestion,
      evite: result.evite || '',
      opcao_1: result.opcao_1 || '',
      opcao_2: result.opcao_2 || '',
      audio: result.audio || '',
      duracao_ms: durationMs
    });

    renderResults(result);
  } catch (err) {
    console.error('Erro na requisição:', err);
    trackGA('erro_analise', {
      pergunta: lastSubmittedQuestion,
      erro_mensagem: err.message
    });
    showToast('Erro ao conectar com o servidor. Tente novamente.');
  } finally {
    submitBtn.disabled = false;
    loadingBox.style.display = 'none';
  }
}

// 7. Renderização dos Resultados
function renderResults(data) {
  const resultsWrapper = document.getElementById('resultsWrapper');
  const eviteContent = document.getElementById('eviteContent');
  const op1Content = document.getElementById('op1Content');
  const op2Content = document.getElementById('op2Content');
  const audioContent = document.getElementById('audioContent');

  const eviteCard = document.getElementById('eviteCard');
  const op1Card = document.getElementById('op1Card');
  const op2Card = document.getElementById('op2Card');
  const audioCard = document.getElementById('audioCard');

  // Evite
  if (data.evite) {
    eviteContent.textContent = data.evite;
    eviteCard.style.display = 'flex';
  } else {
    eviteCard.style.display = 'none';
  }

  // Opção 1
  if (data.opcao_1) {
    op1Content.textContent = data.opcao_1;
    op1Card.style.display = 'flex';
  } else {
    op1Card.style.display = 'none';
  }

  // Opção 2
  if (data.opcao_2) {
    op2Content.textContent = data.opcao_2;
    op2Card.style.display = 'flex';
  } else {
    op2Card.style.display = 'none';
  }

  // Áudio
  if (data.audio) {
    audioContent.textContent = `"${data.audio}"`;
    audioCard.style.display = 'flex';
  } else {
    audioCard.style.display = 'none';
  }

  resultsWrapper.style.display = 'flex';
  resultsWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 8. Copiar Conteúdo
function copyCardContent(elementId, btnElement) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const text = el.textContent.replace(/^"|"$/g, '');

  // Rastreia no Google Analytics qual resposta foi copiada pelo voluntário
  trackGA('resposta_copiada', {
    tipo_resposta: elementId.replace('Content', ''),
    texto_copiado: text,
    pergunta_origem: lastSubmittedQuestion
  });

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      triggerCopySuccess(btnElement);
    }).catch(() => {
      fallbackCopy(text, btnElement);
    });
  } else {
    fallbackCopy(text, btnElement);
  }
}

function fallbackCopy(text, btnElement) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
    triggerCopySuccess(btnElement);
  } catch (err) {
    alert('Erro ao copiar automaticamente. Selecione e copie o texto.');
  }
  document.body.removeChild(textarea);
}

function triggerCopySuccess(btnElement) {
  showToast('Copiado! Pronto para colar no WhatsApp. ✓');
  if (btnElement) {
    const originalText = btnElement.innerHTML;
    btnElement.classList.add('copied');
    btnElement.innerHTML = '✓ Copiado!';
    setTimeout(() => {
      btnElement.classList.remove('copied');
      btnElement.innerHTML = originalText;
    }, 2000);
  }
}

// 9. Compartilhar Direto no WhatsApp
function shareWhatsApp(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const text = el.textContent.trim();

  // Rastreia clique de compartilhamento no WhatsApp
  trackGA('compartilhar_whatsapp', {
    tipo_resposta: elementId.replace('Content', ''),
    texto_compartilhado: text,
    pergunta_origem: lastSubmittedQuestion
  });

  const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

// 10. Toast Notification
function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}
