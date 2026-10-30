// Taxas do Asaas repassadas ao cliente. Ajuste via variável TAXAS_JSON na Vercel se a sua conta tiver taxas diferentes.
// Formato: {"card1":{"pct":2.99,"fixo":0.49},"card2_6":{"pct":3.49,"fixo":0.49},"card7_12":{"pct":3.99,"fixo":0.49},"boleto":0,"pix":0,"maxParcelas":12,"parcelaMinima":30}
const PADRAO = { card1:{pct:2.99,fixo:0.49}, card2_6:{pct:3.49,fixo:0.49}, card7_12:{pct:3.99,fixo:0.49}, boleto:0, pix:0, maxParcelas:12, parcelaMinima:30 };
function taxas(){ try { return Object.assign({}, PADRAO, JSON.parse(process.env.TAXAS_JSON||'{}')); } catch(e){ return PADRAO; } }
// retorna {total, taxa, parcela, n} para um valor base (produtos + frete)
function calcular(base, metodo, n){
  const T = taxas(); base = Math.round(base*100)/100;
  if (metodo === 'PIX')    return { total: base, taxa: T.pix,   n: 1, parcela: base };
  if (metodo === 'BOLETO') return { total: base + T.boleto, taxa: T.boleto, n: 1, parcela: base + T.boleto };
  n = Math.max(1, Math.min(T.maxParcelas, parseInt(n||1,10)||1));
  const f = n===1 ? T.card1 : n<=6 ? T.card2_6 : T.card7_12;
  // taxa cobrada sobre o total; total = (base + fixo) / (1 - pct/100) para o cliente pagar a taxa inteira
  const total = Math.round(((base + f.fixo) / (1 - f.pct/100))*100)/100;
  return { total, taxa: Math.round((total-base)*100)/100, n, parcela: Math.round((total/n)*100)/100 };
}
module.exports = { taxas, calcular };
