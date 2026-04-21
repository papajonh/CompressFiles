import os
import tarfile
from shutil import copyfileobj
import gzip
import sys
import subprocess

def is_tqdm_installed():
    """Verifica se a biblioteca tqdm está instalada."""
    try:
        import tqdm  # Tenta importar a biblioteca
        return True
    except ImportError:
        return False

def install_tqdm():
    """Instala a biblioteca tqdm usando pip."""
    print("A biblioteca 'tqdm' não está instalada. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "tqdm"])

def compress_file(input_path, output_path):
    """Comprime um arquivo individual usando gzip."""
    with open(input_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            total_size = os.path.getsize(input_path)
            if has_tqdm:
                from tqdm import tqdm
                pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Comprimindo {os.path.basename(input_path)}")
            while True:
                buf = f_in.read(8192)
                if not buf:
                    break
                f_out.write(buf)
                if has_tqdm:
                    pbar.update(len(buf))
            if has_tqdm:
                pbar.close()

def decompress_file(input_path, output_path):
    """Descomprime um arquivo .gz usando gzip."""
    with gzip.open(input_path, 'rb') as f_in:
        total_size = os.path.getsize(input_path)
        if has_tqdm:
            from tqdm import tqdm
            pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Descomprimindo {os.path.basename(input_path)}")
        with open(output_path, 'wb') as f_out:
            while True:
                buf = f_in.read(8192)
                if not buf:
                    break
                f_out.write(buf)
                if has_tqdm:
                    pbar.update(len(buf))
            if has_tqdm:
                pbar.close()

def compress_folder(folder_path, output_path, compression_method='gzip'):
    """Comprime uma pasta inteira em um arquivo .tar.gz/.tar.bz2/.tar.xz."""
    if compression_method == 'gzip':
        mode = ':gz'
    elif compression_method == 'bzip2':
        mode = ':bz2'
    elif compression_method == 'xz':
        mode = ':xz'
    else:
        raise ValueError("Método de compressão inválido! Escolha entre 'gzip', 'bzip2' ou 'xz'.")
    
    with tarfile.open(output_path, f'w{mode}') as tar:
        total_size = sum(os.path.getsize(os.path.join(root, file)) for root, dirs, files in os.walk(folder_path) for file in files)
        
        if has_tqdm:
            from tqdm import tqdm
            pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Comprimindo {os.path.basename(folder_path)}")
        
        def progress_callback(tarinfo):
            if has_tqdm:
                pbar.update(tarinfo.size)
            return tarinfo
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                
                tar.add(file_path, arcname=arcname, filter=progress_callback)
        
        if has_tqdm:
            pbar.close()

def decompress_folder(input_path, output_folder):
    """Descomprime uma pasta comprimida em um arquivo .tar.gz/.tar.bz2/.tar.xz."""
    with tarfile.open(input_path, 'r') as tar:
        total_size = sum(tarinfo.size for tarinfo in tar.getmembers())
        
        if has_tqdm:
            from tqdm import tqdm
            pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Descomprimindo {os.path.basename(input_path)}")
        
        def progress_callback(members):
            for member in members:
                yield member
                if has_tqdm:
                    pbar.update(member.size)
        
        tar.extractall(path=output_folder, members=progress_callback(tar.getmembers()))
        
        if has_tqdm:
            pbar.close()

def get_files():
    return [name for name in os.listdir('.') if not name.startswith('.')]

def main():
    global has_tqdm
    has_tqdm = is_tqdm_installed()
    
    if not has_tqdm:
        install_tqdm()
        has_tqdm = True

    while True:
        print("\n" + "=" * 60)
        print("🔧 COMPRESSOR DE ARQUIVOS E PASTAS")
        print("=" * 60)
        print("1. Comprimir arquivo/pasta")
        print("2. Descomprimir arquivo/pasta")
        print("3. Sair")
        
        choice = input("\nEscolha uma opção (1-3): ").strip()
        
        if choice == '1':
            files = get_files()
            
            if not files:
                print("⚠️  Nenhum arquivo encontrado no diretório atual!")
                continue
            
            print("\n📁 Arquivos e pastas disponíveis neste diretório:")
            print("-" * 60)
            for i, file in enumerate(files):
                size = os.path.getsize(file) if os.path.isfile(file) else 0
                if os.path.isdir(file):
                    print(f"  {i+1:2d}. [PASTA] {file:<35} ({size} bytes)")
                else:
                    print(f"  {i+1:2d}. {file:<40} ({size} bytes)")
            
            try:
                file_choice = int(input("\nDigite o número do arquivo/pasta para comprimir (1-{}): ".format(len(files)))) - 1
                if 0 <= file_choice < len(files):
                    input_path = files[file_choice]
                else:
                    print(f"❌ Opção inválida! Escolha um número entre 1 e {len(files)}")
                    continue
            except ValueError:
                print("❌ Entrada inválida! Digite um número.")
                continue
            
            if os.path.isdir(input_path):
                print("\n🗜️  Comprimindo pasta...")
                
                while True:
                    method_choice = input("Escolha o método de compressão (gzip, bzip2, xz): ").strip().lower()
                    if method_choice in ['gzip', 'bzip2', 'xz']:
                        break
                    else:
                        print(f"❌ Método inválido! Escolha entre 'gzip', 'bzip2' ou 'xz'.")
                
                output_path = input_path + f'.tar.{method_choice}'
                compress_folder(input_path, output_path, method_choice)
                print(f"\n✅ Pasta '{input_path}' foi compactada em '{output_path}'.")
            else:
                print("\n🗜️  Comprimindo arquivo...")
                output_path = input_path + '.gz'
                compress_file(input_path, output_path)
                print(f"\n✅ Arquivo '{input_path}' foi compactado em '{output_path}'.")
        
        elif choice == '2':
            tar_files = [name for name in os.listdir('.') if name.endswith('.tar.gz') or name.endswith('.tar.bz2') or name.endswith('.tar.xz')]
            
            if not tar_files:
                print("⚠️  Nenhum arquivo comprimido (.tar.gz, .tar.bz2, .tar.xz) encontrado!")
                continue
            
            print("\n📁 Arquivos comprimidos disponíveis:")
            print("-" * 60)
            for i, file in enumerate(tar_files):
                size = os.path.getsize(file)
                print(f"  {i+1:2d}. {file:<40} ({size} bytes)")
            
            try:
                file_choice = int(input("\nDigite o número do arquivo para descomprimir (1-{}): ".format(len(tar_files)))) - 1
                if 0 <= file_choice < len(tar_files):
                    input_path = tar_files[file_choice]
                else:
                    print(f"❌ Opção inválida! Escolha um número entre 1 e {len(tar_files)}")
                    continue
            except ValueError:
                print("❌ Entrada inválida! Digite um número.")
                continue
            
            output_folder = input("Digite o nome da pasta de saída para a descompressão: ").strip()
            
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            print("\n🔄 Descomprimindo pasta...")
            decompress_folder(input_path, output_folder)
            print(f"\n✅ Pasta '{input_path}' foi descompactada em '{output_folder}'.")
        
        elif choice == '3':
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
