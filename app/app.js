//import express from 'express';
import http from 'http';
import pkg from 'pg';
import path from 'path';



const hostname = 'localhost';
const PORT = 5000;
//const app = express();


//var query = 'select * from "dat_Profiles"';

var __dirname = path.resolve();

const server = http.createServer((req, res) => {
	//console.log(req.query.text);
	// res.sendFile(path.join(__dirname+'/index.html'));
	//res.status(200).json('Сервер работает! ٩(｡•́‿•̀｡)۶');

	let data = []
	req.on('data', chunk => {
		data.push(chunk)
	});

	req.on('end', () => {
		var jdata = JSON.parse(data)
		console.log(jdata)

		if (data.length > 0) {
			var query = `select ${jdata.query} from "${jdata.table}"`;
			console.log(query)

			const { Client } = pkg;
			const client = new Client ({
				user: 'postgres',
				host: 'localhost',
				database: 'soil_database',
				password: 'Magrit',
				port: 5432,
			})
			client.connect()

			client.query(query, (error, dbdata) => {
				client.end();
				console.log(dbdata.rows);
				res.statusCode = 200;
				res.setHeader('Content-Type', 'application/json');
				res.end(JSON.stringify(dbdata.rows));
			})
		} else {
			res.statusCode = 200;
			res.setHeader('Content-Type', 'application/json');
			res.end(JSON.stringify({status: 'empty'}));
		}
	})
})


server.listen(PORT, hostname, () => {
	console.log(`Server running at http://${hostname}:${PORT}/`);
});

