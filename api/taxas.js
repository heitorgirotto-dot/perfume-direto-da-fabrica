const { taxas } = require('./_taxas');
module.exports = (req,res) => { res.setHeader('Cache-Control','public, max-age=300'); res.json(taxas()); };
