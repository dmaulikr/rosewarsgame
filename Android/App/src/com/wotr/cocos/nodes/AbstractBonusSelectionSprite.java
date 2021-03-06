package com.wotr.cocos.nodes;

import org.cocos2d.actions.base.CCRepeatForever;
import org.cocos2d.actions.interval.CCScaleTo;
import org.cocos2d.actions.interval.CCSequence;
import org.cocos2d.nodes.CCSprite;

import com.wotr.model.unit.attribute.bonus.BonusAward;

public abstract class AbstractBonusSelectionSprite extends CCSprite {

	private BonusAward bonusAward;

	public AbstractBonusSelectionSprite(String fileName) {
		super(fileName);

		CCScaleTo scaleUpAction = CCScaleTo.action(0.5f, 1.2f);
		CCScaleTo scaleDownAction = CCScaleTo.action(0.5f, 0.8f);

		CCSequence sequence = CCSequence.actions(scaleUpAction, scaleDownAction);

		CCRepeatForever repeatAction = CCRepeatForever.action(sequence);
		runAction(repeatAction);
	}	

	public BonusAward getBonusAward() {
		return bonusAward;
	}

	public void setBonusAward(BonusAward bonusAward) {
		this.bonusAward = bonusAward;
	}

}
