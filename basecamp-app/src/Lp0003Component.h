#pragma once

#include <QObject>
#include <QQuickWidget>

#include "IComponent.h"

class Lp0003Component final : public QObject, public IComponent {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID IComponent_iid FILE "../metadata.json")
    Q_INTERFACES(IComponent)

public:
    QString id() const override;
    QString displayName() const override;
    QWidget* createWidget(QWidget* parent = nullptr) override;
};
