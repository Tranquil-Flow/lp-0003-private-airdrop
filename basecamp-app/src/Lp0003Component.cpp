#include "Lp0003Component.h"

#include <QUrl>

QString Lp0003Component::id() const {
    return QStringLiteral("lp0003-private-airdrop");
}

QString Lp0003Component::displayName() const {
    return QStringLiteral("LP-0003 Private Airdrop");
}

QWidget* Lp0003Component::createWidget(QWidget* parent) {
    auto* widget = new QQuickWidget(parent);
    widget->setResizeMode(QQuickWidget::SizeRootObjectToView);
    widget->setSource(QUrl(QStringLiteral("qrc:/lp0003/qml/Main.qml")));
    return widget;
}
