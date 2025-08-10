import CryptoJS from 'crypto-js';

class ParadoxAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  async submitResponse(token, round_id, answer, meta) {
    const payload = { token, round_id, answer, meta };
    const payloadStr = JSON.stringify(payload);
    
    // Generate HMAC signature
    const signature = CryptoJS.HmacSHA256(
      payloadStr, 
      process.env.REACT_APP_HMAC_SECRET
    ).toString(CryptoJS.enc.Hex);
    
    const response = await fetch(`${this.baseURL}/respond`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Payload-Signature': signature
      },
      body: payloadStr
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  async newSession() {
    const response = await fetch(`${this.baseURL}/session`, {
      method: 'POST'
    });
    return response.json();
  }
}

export default new ParadoxAPI();
