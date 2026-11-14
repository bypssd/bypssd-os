#include <QApplication>
#include <QStyleFactory>
#include <QStyle>
#include <QDebug>
int main(int argc, char **argv) {
    QApplication app(argc, argv);
    qInfo() << "Available styles:" << QStyleFactory::keys();
    QStyle *style = QStyleFactory::create("BYPSSD");
    if (!style) return 1;
    QApplication::setStyle(style);
    qInfo() << "BYPSSD style loaded successfully:" << style->metaObject()->className();
    return 0;
}
