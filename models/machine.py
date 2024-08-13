import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import seaborn as sns
import joblib  # Para salvar o modelo em um arquivo .pkl

# Carregar o dataset
faces = fetch_lfw_people(min_faces_per_person=60, resize=0.4)

sample_size = 100  # Por exemplo, use 100 amostras

# Obter as dimensões das imagens no dataset
image_shape = faces.images[:sample_size][0].shape
print(f"Tamanho da imagem: {image_shape}")

print("------------------------------------")




# Visualização de algumas faces do dataset
fig, ax = plt.subplots(3, 6, figsize=(15, 10))
for i, axi in enumerate(ax.flat):
    axi.imshow(faces.images[i], cmap='bone')
    axi.set(xticks=[], yticks=[])
    axi.set_xlabel(faces.target_names[faces.target[i]])
plt.show()

# Criação da Máquina Preditiva com SVC e PCA
pca = PCA(n_components=150, whiten=True, random_state=7)
svc = SVC(kernel='rbf', class_weight='balanced')
model = make_pipeline(pca, svc)

# Separação dos Dados de Treino e Teste
X_train, X_test, y_train, y_test = train_test_split(faces.data, faces.target, test_size=0.3, random_state=7)

# Tunning de Hyperparâmetro
param_grid = {'svc__C': [1, 5, 10, 50],
              'svc__gamma': [0.0001, 0.0005, 0.001, 0.005]}
grid = GridSearchCV(model, param_grid)

# Cálculo dos Melhores Hiperparâmetros
grid.fit(X_train, y_train)
print("Melhores Hiperparâmetros:", grid.best_params_)

# Visualizando o resultado do Tunning
best_model = grid.best_estimator_
print("Modelo treinado")

# Treinando a Máquina Preditiva
yfit = best_model.predict(X_test)

# Resultado do Treinamento
fig, ax = plt.subplots(4, 6, figsize=(15, 10))
for i, axi in enumerate(ax.flat):
    axi.imshow(X_test[i].reshape(faces.images.shape[1:]), cmap='bone')  # Usar as dimensões corretas
    axi.set(xticks=[], yticks=[])
    axi.set_ylabel(faces.target_names[yfit[i]].split()[-1],
                   color='blue' if yfit[i] == y_test[i] else 'red')
fig.suptitle('Nomes Preditos Incorretamente em Vermelho', size=14)
plt.show()

# Avaliação com o Classification Report
print(classification_report(y_test, yfit, target_names=faces.target_names))

# Avaliação com a Confusion Matrix
mat = confusion_matrix(y_test, yfit)
sns.heatmap(mat.T, square=True, annot=True, fmt='d', cbar=False,
            xticklabels=faces.target_names,
            yticklabels=faces.target_names)
plt.xlabel('Foto Real - true label')
plt.ylabel('Predito pela Máquina')
plt.show()

# Avaliação com o Accuracy Score
resultado = accuracy_score(y_test, yfit)
print(f"Accuracy: {resultado:.2f}")

# Caminho para salvar o modelo
model_path = 'modelo_reconhecimento_facial.pkl'
print(f"Salvando o modelo como '{model_path}'")

# Salvando o modelo treinado em um arquivo .pkl
try:
    joblib.dump(best_model, model_path)
    print(f"Modelo salvo como '{model_path}'")
except Exception as e:
    print(f"Erro ao salvar o modelo: {e}")


print("------------------------------------")