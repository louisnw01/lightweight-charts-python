// import { Handler } from "../general/handler"



// interface Command {
//     type: string,
//     id: string,
//     method: string,
//     args: string,
    
// }

// class Interpreter {
//     private _tokens: string[];
//     private cwd: string;
//     private _i: number;

//     private objects = {};

//     constructor() {

//     }

//     private _next() {
//         this._i++;
//         this.cwd = this._tokens[this._i];
//         return this.cwd;
//     }

//     private _handleCommand(command: string[]) {
//         const type = this.cwd;
//         switch (this.cwd) {
//             case "auth":
//                 break;
//             case "create":
//                 return this._create();
//             case "obj":
//                 break;
//             case "":
//         }
//     }

//     private static readonly createMap = {
//         "Handler": Handler,
//     }


//     // create, HorizontalLine, id
//     private _create() {
//         const type = this.cwd;
//         this._next();

//         Interpreter.createMap[type](...this.cwd)
//     }

//     private _obj() {
//         const id = this._next();
//         const method = this._next();
//         const args = this._next();
//         this.objects[id][method](args);
//     }
// }