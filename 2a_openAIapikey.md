## Creación de la API key

Para crear la API key en openAI, debe ingresar con su cuenta a la página de openAI https://openai.com/ e ingresar al link API.

 <div align="center">
  <a>
    <img src="imgs/key1.png">
  </a>
  </div>

Ingresar a ``View API keys`` 

   <div align="center">
  <a>
    <img src="imgs/key2.png">
  </a>
  </div>

  En esta nueva pantalla, deben ingresar a su perfil debe hacer clic en ``Create new secret key`` 

![Apikey1](https://github.com/user-attachments/assets/14db0431-3239-432b-bd55-615a7e5bfebe)

  Luego deben verificar su cuenta y crean su propia llave asociada a su cuenta de OpenAI

  ![image](https://github.com/user-attachments/assets/1cc40150-fa69-470c-b41d-308d5d9bb3a9)


  Allí debe ingresar un nombre para su API key, por ejemplo ``workshop3``
  
   <div align="center">
  <a>
    <img src="imgs/key4.png">
  </a>
  </div>

Copie la API key y haga clic en ``Done``. Tenga en cuenta que después de cerrar esta ventana no tendrá de nuevo acceso a esta llave, por lo que debe almacenarla en algún documento.

![image](https://github.com/user-attachments/assets/2696550b-b0aa-4421-80de-123b17b3fb1e)

Almacene su API key en un documento ``.env``, por ejemplo ``api_keys.env``. Esto lo puede hacer en un editor de texto como Sublime o VScode 

La estructura del archivo .env debe ser la siguiente:

````shell
openai_api_key = "skXXXXXXXXXXX"
````

   <div align="center">
  <a>
    <img src="imgs/key6b.png">
  </a>
  </div>
  
Almacene este archivo en la carpeta raíz del proyecto

   <div align="center">
  <a>
    <img src="imgs/key7.png">
  </a>
  </div>

Verifique que el archivo ``.gitignore`` está en la raíz del proyecto (__si el archivo ya está creado, puede omitir este paso__). Si no está creado, debe ubicarse en la raíz del proyecto y escribir la instrucción ``echo. > .gitignore``

 <div align="center">
  <a>
    <img src="imgs/key7_5.PNG">
  </a>
 </div>

Abra con un editor de texto el archivo ``.gitignore`` que se encuentra en la raíz del proyecto. En este archivo se deben poner los nombres de los archivos que no queremos que se compartan en el repositorio en GitHub

   <div align="center">
  <a>
    <img src="imgs/key8b.png">
  </a>
  </div>

  De esta forma su API key estará segura y no tendrá que compartirla ni escribirla en ningún otro documento.
