// Catálogo público: produtos ativos no formato do site.
const db = require('./_db');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  try {
    const rows = await db.select('produtos', 'select=id,marca,nome,genero,preco,notas,lembra,descricao,fotos,ativo,mais_vendido,top5&ativo=is.true&order=id.asc&limit=2000');
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=600');
    res.status(200).json(rows.map(db.toSite));
  } catch (e) {
    res.setHeader('Cache-Control', 'no-store');
    res.status(503).json({ error: e.message });
  }
};
