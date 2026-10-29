// Cotação de frete. Com SUPERFRETE_TOKEN definido na Vercel, consulta a SuperFrete (PAC/SEDEX oficiais dos Correios).
// Sem token, devolve uma estimativa regional (ajuste a tabela abaixo conforme sua experiência).
// Variáveis: SUPERFRETE_TOKEN (opcional), ORIGEM_CEP (padrão 01310-100), PESO_KG (padrão 0.5)
const TABELA = [ // faixa inicial de CEP (2 dígitos) → [PAC R$, dias, SEDEX R$, dias]
  [["01","02","03","04","05","06","07","08","09"], [19.9, 4, 29.9, 2]],   // Grande SP
  [["10","11","12","13","14","15","16","17","18","19"], [24.9, 5, 36.9, 3]], // SP interior/litoral
  [["20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","80","81","82","83","84","85","86","87","88","89","90","91","92","93","94","95","96","97","98","99"], [29.9, 7, 44.9, 4]], // Sudeste/Sul
  [["70","71","72","73","74","75","76","77","78","79"], [34.9, 8, 54.9, 4]], // Centro-Oeste
  [["40","41","42","43","44","45","46","47","48","49","50","51","52","53","54","55","56","57","58","59","60","61","62","63","64","65"], [39.9, 10, 64.9, 5]], // Nordeste
  [["66","67","68","69"], [49.9, 13, 79.9, 7]], // Norte
];
function estimativa(cep){
  const p=cep.slice(0,2);
  for(const [faixas,v] of TABELA){ if(faixas.includes(p)) return [
    {nome:"PAC", preco:v[0], prazo:v[1], estimativa:true},
    {nome:"SEDEX", preco:v[2], prazo:v[3], estimativa:true}]; }
  return [{nome:"PAC", preco:44.9, prazo:10, estimativa:true},{nome:"SEDEX", preco:69.9, prazo:6, estimativa:true}];
}
module.exports = async (req, res) => {
  const cep = String((req.query||{}).cep||'').replace(/\D/g,'');
  res.setHeader('Cache-Control','no-store');
  if (cep.length!==8) return res.status(400).json({erro:'CEP inválido'});
  const token=process.env.SUPERFRETE_TOKEN, origem=(process.env.ORIGEM_CEP||'01310-100').replace(/\D/g,''), peso=Number(process.env.PESO_KG||0.5);
  if (token) {
    try {
      const r = await fetch('https://api.superfrete.com/api/v0/calculator', {
        method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json','Authorization':'Bearer '+token,'User-Agent':'NotaPerfumaria (notaperfumaria.vercel.app)'},
        body: JSON.stringify({from:{postal_code:origem}, to:{postal_code:cep}, services:'1,2', options:{own_hand:false,receipt:false,insurance_value:0,use_insurance_value:false},
          package:{height:12,width:12,length:17,weight:peso}})
      });
      const data = await r.json();
      const ops = (Array.isArray(data)?data:[]).filter(o=>!o.error&&o.price).map(o=>({nome:o.name, preco:Number(o.price), prazo:o.delivery_time, estimativa:false}));
      if (ops.length) return res.json({cep, opcoes:ops});
      console.error('superfrete', JSON.stringify(data).slice(0,300));
    } catch(e){ console.error(e); }
  }
  res.json({cep, opcoes:estimativa(cep)});
};
